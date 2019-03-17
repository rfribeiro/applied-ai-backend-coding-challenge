#include <iostream>
#include <algorithm>
#include <thread>
#include <chrono>
#include <amqpcpp.h>
#include "conn_handler.h"

int main(void)
{
    ConnHandler handler;
    AMQP::TcpConnection connection(handler,
            AMQP::Address("localhost", 5672,
                          AMQP::Login("guest", "guest"), "/"));
    AMQP::TcpChannel channel(&connection);
    channel.onError([&handler](const char* message)
        {
            std::cout << "Channel error: " << message << std::endl;
            handler.Stop();
        });

    channel.setQos(1);
    channel.declareQueue("translator", AMQP::durable);
    channel.consume("translator")
        .onReceived
        (
            [&channel](const AMQP::Message msg,
                       uint64_t tag,
                       bool redelivered)
            {
                const auto body = msg.message();
                //const auto body = msg.exchange();
                std::cout << "Received: " << body << std::endl;
                // translate message on Marian

                // update database with translated message
                
                std::this_thread::sleep_for(std::chrono::seconds(1));
                //std::cout << "Done" << std::endl;
                channel.ack(tag);
            }
        );
    handler.Start();
    std::cout << "Closing connection." << std::endl;
    connection.close();
    return 0;
}