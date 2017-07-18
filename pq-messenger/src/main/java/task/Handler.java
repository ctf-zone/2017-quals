package task;

import akka.actor.Props;
import akka.actor.UntypedAbstractActor;
import akka.io.Tcp.ConnectionClosed;
import akka.io.Tcp.Received;
import akka.io.TcpMessage;
import akka.util.ByteString;

import java.util.Base64;
import javax.swing.plaf.nimbus.State;

public class Handler extends UntypedAbstractActor {

    private Protocol protocol;

    public enum State {COMMAND, MESSAGE}

    private State state;

    public static Props props(Protocol protocol) {
        return Props.create(Handler.class, protocol);
    }

    public Handler(Protocol protocol) {
        this.protocol = protocol;
    }

    @Override
    public void preStart() throws Exception {
        state = State.COMMAND;
    }

    @Override
    public void onReceive(Object msg) throws Exception {
        if (msg instanceof Received) {

            switch (state) {
                case COMMAND:
                    final String choice = ((Received) msg).data().utf8String().toUpperCase().trim();

                    switch (choice) {
                        case "S":
                            getSender().tell(TcpMessage.write(ByteString.fromArray("Enter message:\n".getBytes())), getSelf());
                            state = State.MESSAGE;
                            break;
                        case "Q":
                            getSender().tell(TcpMessage.write(ByteString.fromArray("Bye-bye\n".getBytes())), getSelf());
                            getContext().stop(getSelf());
                            break;
                    }
                    break;

                case MESSAGE:
                    final String encryptedMessageBase64 = ((Received) msg).data().utf8String().trim();
                    try {
                        byte[] encryptedMessage = Base64.getDecoder().decode(encryptedMessageBase64);
                        byte[] message = protocol.decrypt(encryptedMessage);
                        getSender().tell(TcpMessage.write(ByteString.fromArray("OK\n".getBytes())), getSelf());
                    } catch(Exception e) {
                        getSender().tell(TcpMessage.write(ByteString.fromArray((e.getMessage() + "\n").getBytes())), getSelf());
                    }
                    state = State.COMMAND;
                    getSender().tell(TcpMessage.write(ByteString.fromArray(Messages.MENU.getBytes())), getSelf());
                    break;
            }
        } else if (msg instanceof ConnectionClosed) {
            getContext().stop(getSelf());
        }
    }
}
