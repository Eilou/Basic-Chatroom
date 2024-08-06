package multiple_clients;

// client program

import javax.swing.*;
import java.net.*;
import java.io.*;

public class Client {
    // initialize socket
    private Socket socket = null;

    //the Socket constructor takes the IP address (host) and port on the server
    public Client(String host, int port) {
        // establish a connection
        
        try {
            System.err.println("System starting");
            socket = new Socket(host, port);
            System.out.println("Connected to the server");

            DataInputStream serverIS = new DataInputStream(new BufferedInputStream(socket.getInputStream()));

            // takes input from terminal
            
            BufferedReader clientIS = new BufferedReader(new InputStreamReader(System.in));

            // sends output to the socket
            DataOutputStream serverOS = new DataOutputStream(socket.getOutputStream());

            String line = "";
            while (!line.equals("exit")) {
                line = clientIS.readLine();
                serverOS.writeUTF(line);

                String textFromServer = serverIS.readUTF();
                System.out.println(textFromServer);

            }  
            System.out.println("Closing connection");

        } catch (Exception e) {
            System.out.println(e);
        }
    }

    public static void main(String args[]) {
        Client client = new Client("127.0.0.1", 8765);
    }
}