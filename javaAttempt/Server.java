package multiple_clients;

//Server program

import java.net.*;
import java.io.*;

public class Server {
    private Socket socket = null;
    private ServerSocket server = null;

    // constructor take port number
    public Server(int port) {
        // starts server and waits for a connection
        try {
            
            // create the server socket object
            server = new ServerSocket(port);
            
            System.out.println("Server is running, Welcome to COM1006");
            System.out.println("Waiting for client to connect");
            
            socket = server.accept();
            System.out.println("New client connected");

            // seta up input and output from the client
            DataInputStream clientIS = new DataInputStream(
                    new BufferedInputStream(socket.getInputStream()));
            DataOutputStream clientOS = new DataOutputStream(socket.getOutputStream());

            // handle input from user
            BufferedReader serverIS = new BufferedReader(new InputStreamReader(System.in));
            // server output is just ...print()            
        
            System.err.println("Waiting for client input");
            String line = "";

            /*
             * Read client input
             * Output server side
             * Read server input
             * Output client side
             */
            while (!line.equals("exit")) {
                line = clientIS.readUTF();
                System.out.println(line);

                String textToClient = serverIS.readLine();
                clientOS.writeUTF(textToClient);
            }
            System.out.println("Closing connection");

            // close connection
            socket.close();
            clientIS.close();

        } catch (Exception e) {
            System.out.println(e);
        }
    }

    public static void main(String args[]) {
        Server server = new Server(8765);
    }
}
