#include <iostream>
#include <iomanip>
#include <algorithm>
#include <thread>
#include <chrono>
#include <amqpcpp.h>
#include <pqxx/pqxx>
#include "conn_handler.h"
#include "json.hpp"

// for convenience
using json = nlohmann::json;

const std::string COMMAND = "marian-decoder -m model.npz -v vocab.en vocab.de < ";

std::string exec(const char* cmd) {
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}

bool update_database_status(int id) {
    try
    {
        pqxx::connection c("dbname=translations user=postgres password=postgres hostaddr=127.0.0.1 port=5432");
        if (c.is_open()) {
            std::cout << "Opened database successfully: " << c.dbname() << std::endl;
        } else {
            std::cout << "Can't open database" << std::endl;
         return 1;
        }

        auto sql = "UPDATE translation set status = \'pending\' where ID=1";

        pqxx::work w(c);
        w.exec(sql);
        w.commit();
        std::cout << "Records updated successfully" << std::endl;
    }
    catch (const std::exception &e)
    {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}

int main(void) {

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

                // deserialize object
                auto translation = json::parse(body); 

                update_database_status( translation["id"].get<int>());

                std::cout << "Received: " << body << std::endl;
                std::cout << std::setw(4) << translation << std::endl;
                //std::cout << std::setw(4) << translation["id"] << std::endl;
                
                auto send_command = COMMAND + "\"" + translation["original"].get<std::string>() + "\"";
                std::cout << "Command: " << send_command << std::endl;

                // translate message on Marian
                //std::string translated_msg = exec(send_command.c_str());

                // update database with translated message
                // update_database_translation( translation["id"].get<int>());

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