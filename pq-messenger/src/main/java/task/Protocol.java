package task;

import java.io.ByteArrayOutputStream;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.MessageDigest;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.SecureRandom;
import java.util.Arrays;

import javax.crypto.Cipher;
import javax.crypto.Mac;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;


public class Protocol {
    private SecureRandom random;
    private Cipher ac;
    private KeyPair keyPair;
    private Cipher sc;
    private Mac mac;
    private MessageDigest kdf;

    public Protocol(KeyPair keyPair) throws Exception {
        random = new SecureRandom();
        ac = Cipher.getInstance("McEliece");
        sc = Cipher.getInstance("AES/CBC/PKCS5PADDING");
        mac = Mac.getInstance("HmacSHA256");
        kdf = MessageDigest.getInstance("SHA-256");

        if (keyPair == null) {
            KeyPairGenerator kpg = KeyPairGenerator.getInstance("McEliece");
            kpg.initialize(0, random);
            this.keyPair = kpg.generateKeyPair();
        } else {
            this.keyPair = keyPair;
        }
    }

    public PublicKey getPublicKey() {
        return keyPair.getPublic();
    }

    public PrivateKey getPrivateKey() {
        return keyPair.getPrivate();
    }

    public byte[] encrypt(byte[] in) throws Exception {
        ac.init(Cipher.ENCRYPT_MODE, keyPair.getPublic());

        // Generate and encrypt token
        byte[] token = new byte[ac.getBlockSize()];
        random.nextBytes(token);

        byte[] encryptedToken = ac.doFinal(token);

        // Derive keys
        kdf.reset();

        byte[] digest = kdf.digest(token);

        // Encryption
        byte[] scKey = Arrays.copyOfRange(digest, 0, 16);

        byte[] iv = new byte[sc.getBlockSize()];
        random.nextBytes(iv);

        IvParameterSpec ivSpec = new IvParameterSpec(iv);
        SecretKeySpec scKeySpec = new SecretKeySpec(scKey, "AES");

        sc.init(Cipher.ENCRYPT_MODE, scKeySpec, ivSpec);

        byte[] encryptedData = sc.doFinal(in);

        // HMAC
        byte[] macKey = Arrays.copyOfRange(digest, 16, 32);

        SecretKeySpec macKeySpec = new SecretKeySpec(macKey, "HmacSHA256");

        mac.reset();
        mac.init(macKeySpec);
        mac.update(iv);
        mac.update(encryptedData);

        byte[] macDigest = new byte[mac.getMacLength()];
        mac.doFinal(macDigest, 0);

        // Final
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();

        outputStream.write(encryptedToken);
        outputStream.write(iv);
        outputStream.write(encryptedData);
        outputStream.write(macDigest);

        return outputStream.toByteArray();
    }

    public byte[] decrypt(byte[] in) throws Exception {
        ac.init(Cipher.DECRYPT_MODE, keyPair.getPrivate());

        int minLength = ac.getBlockSize() + 2 * sc.getBlockSize() + mac.getMacLength();

        if (in.length < minLength) {
            throw new ProtocolException("Message is too small!");
        }

        byte[] encryptedToken = Arrays.copyOfRange(in, 0, ac.getBlockSize());
        byte[] iv = Arrays.copyOfRange(in, ac.getBlockSize(), ac.getBlockSize() + sc.getBlockSize());
        byte[] encryptedData = Arrays.copyOfRange(in, ac.getBlockSize() + sc.getBlockSize(), in.length - mac.getMacLength());
        byte[] macDigest = Arrays.copyOfRange(in, in.length - mac.getMacLength(), in.length);

        // Decrypt token
        byte[] token = ac.doFinal(encryptedToken);

        // Derive keys
        kdf.reset();

        byte[] digest = kdf.digest(token);

        // HMAC verify
        byte[] macKey = Arrays.copyOfRange(digest, 16, 32);
        SecretKeySpec macKeySpec = new SecretKeySpec(macKey, "HmacSHA256");

        mac.reset();
        mac.init(macKeySpec);
        mac.update(iv);
        mac.update(encryptedData);

        byte[] macDigestComputed = new byte[mac.getMacLength()];
        mac.doFinal(macDigestComputed, 0);

        if (!Arrays.equals(macDigest, macDigestComputed)) {
            throw new ProtocolException("Message HMAC mismatch!");
        }

        // Decrypt
        byte[] scKey = Arrays.copyOfRange(digest, 0, 16);

        IvParameterSpec ivSpec = new IvParameterSpec(iv);
        SecretKeySpec scKeySpec = new SecretKeySpec(scKey, "AES");

        sc.init(Cipher.DECRYPT_MODE, scKeySpec, ivSpec);

        byte[] data = sc.doFinal(encryptedData);

        return data;
    }
}
