import React, { useEffect, useRef, useState } from "react";
import "./App.css";
import { FaComputer } from "react-icons/fa6";
import { IoSend } from "react-icons/io5";
import { GoogleGenerativeAI } from "@google/generative-ai";

const App = () => {
  const [message, setmessage] = useState("");
  const [isResponseScreen, setisResponseScreen] = useState(false);
  const [messages, setmessages] = useState([]);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  const hitRequest = () => {
    if (message) {
      generateResponse(message);
    } else {
      alert("You must write something...!");
    }
  };

  const newChat = () => {
    setisResponseScreen(false);
    setmessages([]);
  }

  const generateResponse = async (msg) => {

    if(!msg) return;


    const genAI = await new GoogleGenerativeAI(
      "AIzaSyC6SJCRqUJG12jQcXFzHuyWiiYPSK8Qzvs"
    );
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
    const result = await model.generateContent(msg);

    const newMessages = [
      ...messages,
      {
        type: "userMsg",
        text: msg,
      },
      {
        type: "responseMsg",
        text: result.response.text()
      }  
    ]

    setmessages(newMessages);
    setisResponseScreen(true);
    setmessage("");
    console.log(result.response.text());
  };

  return (
    <div>
      <div className="container w-screen min-h-screen overflow-x-hidden bg-[#142238] text-white">
        {isResponseScreen ? (
          <div className="middle h-[80vh]">
            <div className="header flex items-center py-[25px] justify-between w-[100vw] px-[300px]">
              <h2 className="text-2xl">Tech Trekkers</h2>
              <button
                id="chatBtn"
                className="p-[10px] rounded-[10px] cursor-pointer bg-white  text-blue-400 px-[10px]"
                onClick={newChat}
              >
                New Chat
              </button>
            </div>
            <div className="messages overflow-y-auto max-h-[60vh]">
              {
              messages?.map((msg, index) => {
                return (
                  <div key={index} className={msg.type}>{msg.text}</div>
                )
              })
            }
              {/* <div className="userMsg">Helllooooo!!!!</div>
              <div className="responseMsg">Hii! How can I help you?</div> */}
              <div ref={messagesEndRef}/>
            </div >
          </div>
        ) : (
          <div className="middle h-[80vh] flex items-center flex-col justify-center ">
            <h1 className="text-5xl">Hey! Wanna scrap Linkedin?</h1>

            <div className="boxes mt-10 flex items-center gap-2">
              <div className="card px-[20px] rounded-lg cursor-pointer transition-all hover:bg-[#ffffff] relative min-h-[20vh] p-[10px] bg-[#abb8da]">
                <p className="text-[20px] text-black">
                  Find the Computer Science
                  <br /> Companies for me.
                </p>
                <i className="absolute right-3 bottom-3 text-[18px] text-black">
                  <FaComputer />
                </i>
              </div>
              <div className="card px-[20px] rounded-lg cursor-pointer transition-all hover:bg-[#ffffff] relative min-h-[20vh] p-[10px] bg-[#abb8da]">
                <p className="text-[20px] text-black">
                  I want to know educational<br /> background of
                   Mr. Ratan Tata.
                </p>
                <i className="absolute right-3 bottom-3 text-[18px] text-black">
                  <FaComputer />
                </i>
              </div>
              <div className="card px-[20px] rounded-lg cursor-pointer transition-all hover:bg-[#ffffff] relative min-h-[20vh] p-[10px] bg-[#abb8da]">
                <p className="text-[20px] text-black">
                  Is there any Job updates <br /> for me?
                </p>
                <i className="absolute right-3 bottom-3 text-[18px] text-black">
                  <FaComputer />
                </i>
              </div>
              <div className="card px-[20px] rounded-lg cursor-pointer transition-all hover:bg-[#ffffff] relative min-h-[20vh] p-[10px] bg-[#abb8da]">
                <p className="text-[20px] text-black">
                  Find the Business analyst
                  <br /> profiles for me.
                </p>
                <i className="absolute right-3 bottom-3 text-[18px] text-black">
                  <FaComputer />
                </i>
              </div>
            </div>
          </div>
        )}

        <div className="bottom w-[100%] flex flex-col items-center ">
          <div className="inputBox w-[60%] py-[5px] flex items-center bg-[#ffffff] rounded-[30px]">
            <input
              onChange={(e) => {
                setmessage(e.target.value);
              }}
              value={message}
              type="text"
              className="p-[10px] pl-[20px] bg-transparent flex-1 border-none outline-none text-black"
              placeholder="Write your message here..."
              id="messageBox"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  hitRequest();
                }
              }}
            ></input>
            {message == "" ? (
              ""
            ) : (
              <i
                className="text-blue-600 mr-5 cursor-pointer text-[20px]"
                onClick={hitRequest}
              >
                <IoSend />
              </i>
            )}
          </div>
          <p className="mt-3">
            This chatbot is created by Tech Trekkers. This chatbot uses
            LinkedinApi.
          </p>
        </div>
      </div>
    </div>
  );
};

export default App;
