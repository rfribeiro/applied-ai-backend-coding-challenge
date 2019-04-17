#include <iostream>
#include <iomanip>
#include <algorithm>
#include <thread>
#include <chrono>
#include <sstream>
#include <fstream>
//#include <pstream.h>
#include <amqpcpp.h>
#include <pqxx/pqxx>
#include "conn_handler.h"
#include "json.hpp"

// for convenience
using json = nlohmann::json;

class Translator  {

    private:
        std::string translation_command;

    public:
        //const std::string TRANSLATOR = "marian-decoder -m model.npz -v vocab.en vocab.de < ";
        static constexpr const char* TRANSLATOR = "./amun -m en-de/model.npz -s en-de/vocab.en.json -t en-de/vocab.de.json";
        static constexpr const char* ECHO = "echo ";
        static constexpr const char* QM = "\"";
        static constexpr const char* PIPE = "|";

        Translator(json tr_configuration)  {
            try {
                this->translation_command = tr_configuration["command"];
                std::cout << translation_command << std::endl;
            }
            catch (const std::exception &e)
            { 
                this->translation_command = Translator::TRANSLATOR;
            }
        }

        const std::string translate(const std::string original) {

            std::array<char, 128> buffer;
            std::string result_str;
            auto command = std::string(Translator::ECHO) + Translator::QM + original + Translator::QM \
                    + Translator::PIPE + translation_command;
            std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
            if (!pipe) {           
                throw std::runtime_error("popen() failed!");
            }
            while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
                result_str += buffer.data();
            }
            return result_str;
        }  
};

class TranslatorDatabase {

    private: 
        std::string strConnection;

    public:
        static constexpr const char* STATUS_PENDING = "pending";
        static constexpr const char* STATUS_SUCCESS = "success";

        TranslatorDatabase(json db_configuration) {
            this->strConnection = "dbname=" + db_configuration["dbname"].get<std::string>() \
                        + " user=" + db_configuration["user"].get<std::string>() \
                        + " password=" + db_configuration["password"].get<std::string>() \
                        + " host=" + db_configuration["hostname"].get<std::string>() \
                        + " port=" + std::to_string(db_configuration["port"].get<int>());
            //std::cout << "DB :" << this->strConnection << std::endl;
        }

        const bool update_status(int id, const char* status) {

            bool bReturn = true;
            try
            {
                pqxx::connection c(strConnection.c_str());
                if (c.is_open()) {
                    std::cout << "Opened database successfully: " << c.dbname() << std::endl;

                    auto sql = "UPDATE translation set status = \'" + std::string(status) + "\' where ID=" + std::to_string(id);
                    //auto sql = command.str();
                    pqxx::work w(c);
                    w.exec(sql.c_str());
                    w.commit();
                    std::cout << "Records updated successfully" << std::endl;

                } else {
                    throw std::runtime_error("Error executing SQL");
                }

            }
            catch (const std::exception &e)
            {
                std::cerr << e.what() << std::endl;
                throw std::runtime_error("Can't open database");
            }
            return bReturn;
        }

        const bool  update_translation(int id, std::string translation, int translation_lenght, 
                                                const char* status) {
            bool bReturn = true;
            try
            {
                pqxx::connection c(strConnection.c_str());
                if (c.is_open()) {
                    std::cout << "Opened database successfully: " << c.dbname() << std::endl;

                    auto sql = "UPDATE translation set translated=\'" + translation + "\'" \
                                + ", translated_count = " + std::to_string(translation_lenght)  \
                                + ", status = \'" + std::string(status) + "\'" \
                                + "where ID=" + std::to_string(id);
                    pqxx::work w(c);
                    w.exec(sql.c_str());
                    w.commit();
                    std::cout << "Records updated successfully" << std::endl;

                } else {
                    throw std::runtime_error("Error executing SQL");
                }

            }
            catch (const std::exception &e)
            {
                std::cerr << e.what() << std::endl;
                throw std::runtime_error("Can't open database");
            }
            return bReturn;
        }

};

json read_configuration(const std::string file) {
    std::ifstream ifile(file);
    json j;
    ifile >> j;
    return j;
}

int main(int argc, char **argv) {

    json jConfiguration;

    try {
        jConfiguration = read_configuration(argv[1]);
        std::cout << "Configuration:" << std::endl;
        std::cout << std::setw(4) << jConfiguration << std::endl;
    }
    catch (const std::exception &e) {
        throw std::runtime_error("Fail loading configuration file");
    } 

    ConnHandler handler;
    AMQP::TcpConnection connection(handler,
            AMQP::Address(jConfiguration["rabbit"]["host"].get<std::string>(), jConfiguration["rabbit"]["port"].get<int>(),
                          AMQP::Login(jConfiguration["rabbit"]["user"].get<std::string>(), 
                            jConfiguration["rabbit"]["password"].get<std::string>()), 
                            jConfiguration["rabbit"]["vfolder"].get<std::string>()));
    AMQP::TcpChannel channel(&connection);
    channel.onError([&handler](const char* message)
        {
            std::cout << "Channel error: " << message << std::endl;
            handler.Stop();
        });

    channel.setQos(1);
    channel.declareQueue(jConfiguration["rabbit"]["queue_name"], AMQP::durable);
    channel.consume(jConfiguration["rabbit"]["queue_name"])
        .onReceived
        (
            [&channel, jConfiguration](const AMQP::Message msg,
                       uint64_t tag,
                       bool redelivered)
            {
                try {
                    const auto body = msg.message();
                    //const auto body = msg.exchange();

                    // deserialize object
                    auto translation = json::parse(body); 
                    auto db = TranslatorDatabase(jConfiguration["database"]);
                    db. update_status(translation["id"].get<int>(), 
                                        TranslatorDatabase::STATUS_PENDING);

                    std::cout << "Received: " << body << std::endl;
                    std::cout << std::setw(4) << translation << std::endl;
                    
                    // translate message on Marian
                    auto translator = Translator(jConfiguration["translator"]);
                    auto translated_msg = translator.translate(translation["original"].get<std::string>()); 
                    std::cout << "Translation: " << translated_msg << std::endl;

                    if (!translated_msg.empty()) {
                        // update database with translated message
                        db.update_translation(translation["id"].get<int>(), 
                                                translated_msg, translated_msg.length(), 
                                                TranslatorDatabase::STATUS_SUCCESS);
                    }

                    std::this_thread::sleep_for(std::chrono::seconds(1));
                    std::cout << "Done" << std::endl;
                    channel.ack(tag);
                }
                catch (const std::exception &e)
                {
                    std::cerr << e.what() << std::endl;
                } 
            }
        );

    handler.Start();
    std::cout << "Closing connection." << std::endl;
    connection.close();

    return 0;
}