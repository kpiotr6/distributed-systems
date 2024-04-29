package server;

import java.io.*;

public class ObjectSaver {
    public static void save(Object object, String filename){
        try(FileOutputStream fileOut = new FileOutputStream(filename);
            ObjectOutputStream out = new ObjectOutputStream(fileOut)){
            out.writeObject(object);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    public static Object read(String filename){
        try(FileInputStream fileOut = new FileInputStream(filename);
            ObjectInputStream out = new ObjectInputStream(fileOut)){
            return out.readObject();
        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }
        return null;
    }
    public static void remove(String filename){
        File toRemove = new File(filename);
        toRemove.delete();
    }
}
