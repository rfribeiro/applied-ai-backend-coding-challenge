#include <iostream>
#include <iomanip>
#include <algorithm>
#include <thread>
#include <chrono>
#include <sstream>
//#include <pstream.h>
#include <amqpcpp.h>
#include <pqxx/pqxx>
#include "conn_handler.h"
#include "json.hpp"

// for convenience
using json = nlohmann::json;

class Translator  {

    public:
        //const std::string TRANSLATOR = "marian-decoder -m model.npz -v vocab.en vocab.de < ";
        static constexpr const char* TRANSLATOR = "./amun -m en-de/model.npz -s en-de/vocab.en.json -t en-de/vocab.de.json";
        static constexpr const char* ECHO = "echo ";
        static constexpr const char* QM = "\"";
        static constexpr const char* PIPE = "|";

        static const std::string translate(const std::string original) {

            std::array<char, 128> buffer;
            std::string result_str;
            auto send_command = std::string(Translator::ECHO) + Translator::QM + original + Translator::QM \
                                + Translator::PIPE + Translator::TRANSLATOR;
            std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(send_command.c_str(), "r"), pclose);
            if (!pipe) {           
                throw std::runtime_error("popen() failed!");
            }
            while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
                result_str += buffer.data();
            }
            return result_str;
        }  
};

bool update_database_status(int id, std::string status) {
    try
    {
        pqxx::connection c("dbname=translations user=postgres password=postgres hostaddr=127.0.0.1 port=5432");
        if (c.is_open()) {
            std::cout << "Opened database successfully: " << c.dbname() << std::endl;
        } else {
            std::cout << "Can't open database" << std::endl;
         return 1;
        }

        auto sql = "UPDATE translation set status = \'" + status + "\' where ID=" + std::to_string(id);
        //auto sql = command.str();
        pqxx::work w(c);
        w.exec(sql.c_str());
        w.commit();
        std::cout << "Records updated successfully" << std::endl;
    }
    catch (const std::exception &e)
    {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}

bool update_database_translation(int id, std::string translation, int translation_lenght, std::string status) {
    try
    {
        pqxx::connection c("dbname=translations user=postgres password=postgres hostaddr=127.0.0.1 port=5432");
        if (c.is_open()) {
            std::cout << "Opened database successfully: " << c.dbname() << std::endl;
        } else {
            std::cout << "Can't open database" << std::endl;
         return 1;
        }

        //auto sql = "UPDATE translation set status = \'pending\' where ID=1";
        auto sql = "UPDATE translation set translated=\'" + translation + "\'" \
                                    + ", translated_count = " + std::to_string(translation_lenght)  \
                                    + ", status = \'" + status + "\'" \
                                    + "where ID=" + std::to_string(id);
        pqxx::work w(c);
        w.exec(sql.c_str());
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

                update_database_status( translation["id"].get<int>(), "pending");

                std::cout << "Received: " << body << std::endl;
                std::cout << std::setw(4) << translation << std::endl;
                
                // translate message on Marian
                auto translated_msg = Translator::translate(translation["original"].get<std::string>()); 
                std::cout << "Translation: " << translated_msg << std::endl;

                if (!translated_msg.empty()) {
                    // update database with translated message
                    update_database_translation(translation["id"].get<int>(), translated_msg, translated_msg.length(), "success");
                }

                std::this_thread::sleep_for(std::chrono::seconds(1));
                std::cout << "Done" << std::endl;
                channel.ack(tag);
            }
        );
    handler.Start();
    std::cout << "Closing connection." << std::endl;
    connection.close();

    return 0;
}