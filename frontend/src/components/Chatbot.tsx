import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send, Loader2, Bot, User } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const API_BASE = "http://127.0.0.1:8000";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hi! I'm your Placement AI. Got doubts about your resume, ATs score, or skills? Ask me anything!" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  // Auto scroll
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isOpen]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMsg = input.trim();
    setInput("");
    
    const updatedMsgs: Message[] = [...messages, { role: "user", content: userMsg }];
    setMessages(updatedMsgs);
    setIsLoading(true);
    
    try {
      const res = await fetch(`${API_BASE}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: updatedMsgs }),
      });
      
      const data = await res.json();
      if (res.ok) {
        setMessages([...updatedMsgs, { role: "assistant", content: data.response }]);
      } else {
        setMessages([...updatedMsgs, { role: "assistant", content: "Oops, I encountered an error. Try again!" }]);
      }
    } catch {
      setMessages([...updatedMsgs, { role: "assistant", content: "Failed to connect to the server." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: isOpen ? 0 : 1 }}
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full flex items-center justify-center text-primary-foreground shadow-lg z-50 transition-transform hover:scale-105"
        style={{ background: "var(--gradient-primary)", boxShadow: "var(--shadow-glow)" }}
      >
        <MessageCircle className="w-6 h-6" />
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-6 right-6 w-80 md:w-96 rounded-2xl glass-card border border-border flex flex-col z-50 shadow-2xl overflow-hidden"
            style={{ height: "500px", maxHeight: "80vh" }}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border bg-secondary/30">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-foreground">Placement Assistant</h3>
                  <p className="text-[10px] text-success flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-success"></span> Online
                  </p>
                </div>
              </div>
              <button onClick={() => setIsOpen(false)} className="w-8 h-8 rounded-full flex items-center justify-center text-muted-foreground hover:bg-secondary transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} gap-2`}>
                  {msg.role === "assistant" && (
                    <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                      <Bot className="w-3 h-3 text-primary" />
                    </div>
                  )}
                  <div className={`py-2 px-3.5 rounded-2xl max-w-[80%] text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.role === "user" 
                      ? "bg-primary text-primary-foreground rounded-br-sm" 
                      : "bg-secondary text-foreground rounded-bl-sm"
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start gap-2">
                  <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                    <Bot className="w-3 h-3 text-primary" />
                  </div>
                  <div className="py-3 px-4 rounded-2xl bg-secondary rounded-bl-sm flex items-center gap-1">
                    <motion.div animate={{y:[0,-4,0]}} transition={{repeat:Infinity, duration:0.6}} className="w-1 h-1 bg-muted-foreground rounded-full"/>
                    <motion.div animate={{y:[0,-4,0]}} transition={{repeat:Infinity, duration:0.6, delay:0.2}} className="w-1 h-1 bg-muted-foreground rounded-full"/>
                    <motion.div animate={{y:[0,-4,0]}} transition={{repeat:Infinity, duration:0.6, delay:0.4}} className="w-1 h-1 bg-muted-foreground rounded-full"/>
                  </div>
                </div>
              )}
              <div ref={endRef} />
            </div>

            {/* Input Area */}
            <div className="p-3 border-t border-border bg-background/50">
              <form 
                onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                className="flex items-center gap-2 bg-secondary/50 rounded-full border border-border p-1 pl-4"
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about placements..."
                  className="flex-1 bg-transparent text-sm text-foreground focus:outline-none placeholder:text-muted-foreground"
                />
                <button 
                  type="submit" 
                  disabled={!input.trim() || isLoading}
                  className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground disabled:opacity-50 transition-opacity"
                >
                  <Send className="w-3.5 h-3.5 ml-0.5" />
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Chatbot;
