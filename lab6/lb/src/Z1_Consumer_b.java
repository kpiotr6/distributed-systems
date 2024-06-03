import com.rabbitmq.client.*;

import java.io.IOException;

public class Z1_Consumer_b {

    public static void main(String[] argv) throws Exception {

        // info
        System.out.println("Z1 CONSUMER");

        // connection & channel
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // queue
        String QUEUE_NAME = "queue1";
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);
        channel.basicQos(1);
        // consumer (handle msg)
        Consumer consumer = new DefaultConsumer(channel) {
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
                String message = new String(body, "UTF-8");
                System.out.println("Received: " + message);
                int timeToSleep = Integer.parseInt(message);
                try {
                    Thread.sleep(timeToSleep * 1000);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
                channel.basicAck(envelope.getDeliveryTag(), false);
                System.out.println("Processed: " + message);
            }
        };

        // start listening
        System.out.println("Waiting for messages...");
//        channel.basicConsume(QUEUE_NAME, true, consumer);
        channel.basicConsume(QUEUE_NAME, false, consumer);
        // close
//        channel.close();
//        connection.close();
    }
}
