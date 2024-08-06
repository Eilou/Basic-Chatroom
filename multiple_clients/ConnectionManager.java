package multiple_clients;

import java.io.IOException;
import java.net.Socket;
import java.util.ArrayList;
import java.util.HashMap;

public class ConnectionManager {

    public ArrayList<Socket> connections;

    public ConnectionManager() {
        connections = new ArrayList<>();
    }

    public void connect(Socket socket) {
        connections.add(socket);
    }

    public void disconnect(Socket socket) throws IOException {
        socket.close();
    }

}
