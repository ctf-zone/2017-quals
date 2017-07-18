package task;

import akka.actor.ActorRef;
import akka.actor.ActorSystem;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;

import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.Security;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;
import java.util.List;

import org.bouncycastle.pqc.crypto.mceliece.McElieceCipher;
import org.bouncycastle.pqc.jcajce.provider.BouncyCastlePQCProvider;

import scala.concurrent.Await;
import scala.concurrent.duration.Duration;

public class Main {

    public static final int PORT = 1337;

    @Parameter(names = "--help", description = "Show help", help = true)
    public boolean help;

    @Parameters(commandDescription = "Generate keys and save them to files")
    public static class GenKeysCommand {
        @Parameter(names = "-outdir", description = "Directory where keys will be saved", required = true)
        public String outDir;
    }

    @Parameters(commandDescription = "Encrypt string")
    public static class EncryptCommand {
        @Parameter(names = "-keysdir", description = "Directory with keys", required = true)
        public String keysDir;

        @Parameter(description = "<str>", required = true)
        public String str;
    }

    @Parameters(commandDescription = "Start server")
    public static class StartCommand {
        @Parameter(names = "-keysdir", description = "Directory with keys", required = true)
        public String keysDir;
    }

    public static void main(String[] args) {

        Main main = new Main();
        GenKeysCommand gc = new GenKeysCommand();
        EncryptCommand ec = new EncryptCommand();
        StartCommand sc = new StartCommand();

        JCommander jc = JCommander.newBuilder()
            .addObject(main)
            .addCommand("genkeys", gc)
            .addCommand("encrypt", ec)
            .addCommand("start", sc)
            .build();

        String cmd = null;
        try {
            jc.parse(args);
            cmd = jc.getParsedCommand();
        } catch(Exception e) {
            System.out.println(e.getMessage());
            jc.usage();
            System.exit(1);
        }

        if (main.help || cmd == null) {
            jc.usage();
            System.exit(0);
        }


        Security.addProvider(new BouncyCastlePQCProvider());

        switch(cmd) {
            case "genkeys":
                main.genKeys(gc);
                break;

            case "encrypt":
                main.encrypt(ec);
                break;

            case "start":
                main.start(sc);
                break;
        }

    }

    public void exportPEMObject(byte[] data, String filename, String name) throws IOException {
        FileWriter fw = new FileWriter(filename);

        fw.write(String.format("-----BEGIN %s-----\n", name.toUpperCase()));

        String encoded = Base64.getEncoder().encodeToString(data);
        for (int i = 0; i < encoded.length() / 64; i++) {
            fw.write(encoded.substring(i*64, (i+1)*64) + "\n");
        }
        int rest = encoded.length() % 64;
        fw.write(encoded.substring(encoded.length() - rest, encoded.length()) + "\n");
        fw.write(String.format("-----END %s-----\n", name.toUpperCase()));
        fw.flush();
    }

    public byte[] importPemObject(String filename) throws IOException {
        List<String> lines = Files.readAllLines(Paths.get(filename));
        lines.remove(0);
        lines.remove(lines.size() - 1);
        String encoded = String.join("", lines);

        return Base64.getDecoder().decode(encoded);
    }

    public void genKeys(GenKeysCommand c) {
        try {
            Path dir = Paths.get(c.outDir);
            Protocol protocol = new Protocol(null);

            exportPEMObject(protocol.getPublicKey().getEncoded(),
                    dir.resolve("pubkey.pem").toString(), "Public Key");

            exportPEMObject(protocol.getPrivateKey().getEncoded(),
                    dir.resolve("privkey.pem").toString(), "Private key");

        } catch (Exception e) {
            System.out.println("genkeys error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public Protocol initWithKeys(String keysDir) throws Exception {
            Path dir = Paths.get(keysDir);

            byte[] pubKeyBytes = importPemObject(dir.resolve("pubkey.pem").toString());
            X509EncodedKeySpec pubKeySpec = new X509EncodedKeySpec(pubKeyBytes);

            byte[] privKeyBytes = importPemObject(dir.resolve("privkey.pem").toString());
            PKCS8EncodedKeySpec privKeySpec = new PKCS8EncodedKeySpec(privKeyBytes);

            KeyFactory kf = KeyFactory.getInstance("McEliece");
            KeyPair keyPair = new KeyPair(kf.generatePublic(pubKeySpec),
                    kf.generatePrivate(privKeySpec));

            return new Protocol(keyPair);
    }

    public void encrypt(EncryptCommand c) {
        try {
            Protocol protocol = initWithKeys(c.keysDir);
            byte[] encrypted = protocol.encrypt(c.str.getBytes());
            String encoded = Base64.getEncoder().encodeToString(encrypted);
            System.out.println(encoded);
        } catch (Exception e) {
            System.out.println("encrypt error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void start(StartCommand c) {
        try {

            Protocol protocol = initWithKeys(c.keysDir);

            ActorSystem system = ActorSystem.create("ServerActorSystem");
            ActorRef server = system.actorOf(Server.props(PORT, protocol), "server");
            Await.result(system.whenTerminated(), Duration.Inf());

        } catch (Exception e) {
            System.out.println("start error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
