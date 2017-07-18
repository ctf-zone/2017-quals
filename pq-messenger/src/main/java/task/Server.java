package task;

import akka.actor.ActorRef;
import akka.actor.Props;
import akka.actor.UntypedAbstractActor;
import akka.io.Tcp;
import akka.io.Tcp.CommandFailed;
import akka.io.Tcp.Connected;
import akka.io.TcpMessage;
import akka.util.ByteString;

import java.net.InetSocketAddress;
import java.util.Base64;

public class Server extends UntypedAbstractActor {

    private int port;
    private Protocol protocol;

    public static Props props(int port, Protocol protocol) {
        return Props.create(Server.class, port, protocol);
    }

    public Server(int port, Protocol protocol) {
        this.port = port;
        this.protocol = protocol;
    }

    @Override
    public void preStart() throws Exception {
        final ActorRef tcp = Tcp.get(getContext().system()).manager();

        tcp.tell(TcpMessage.bind(getSelf(),
                    new InetSocketAddress("0.0.0.0", port), 100), getSelf());
    }

    @Override
    public void onReceive(Object msg) throws Exception {
        if (msg instanceof CommandFailed) {
            getContext().stop(getSelf());
        } else if (msg instanceof Connected) {
            final Connected conn = (Connected) msg;

            final ActorRef handler = getContext().actorOf(
                    Handler.props(protocol));

            getSender().tell(TcpMessage.register(handler), getSelf());

            // Hello message
            getSender().tell(TcpMessage.write(ByteString.fromArray(Messages.HELLO.getBytes())), getSelf());

            // Menu
            getSender().tell(TcpMessage.write(ByteString.fromArray(Messages.MENU.getBytes())), getSelf());

        }
    }


}
