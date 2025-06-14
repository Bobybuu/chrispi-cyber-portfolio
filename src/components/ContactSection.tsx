
import { useState } from "react";
import { Button } from "./ui/button";
import { useToast } from "../hooks/use-toast";

const ContactSection = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: ""
  });
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate form submission
    toast({
      title: "Message sent!",
      description: "Thanks for reaching out. I'll get back to you soon.",
    });
    setFormData({ name: "", email: "", message: "" });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <section className="py-20 relative">
      <div className="container mx-auto px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            Get In <span className="neon-text">Touch</span>
          </h2>
          
          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Contact info */}
            <div>
              <div className="glass rounded-2xl p-8">
                <h3 className="text-2xl font-semibold mb-6 text-cyan-400">
                  Let's Connect
                </h3>
                
                <p className="text-white/80 mb-8 leading-relaxed">
                  I'm always interested in discussing new opportunities, 
                  innovative projects, and ways to improve infrastructure and deployment processes. 
                  Whether you need DevOps consulting or want to collaborate on exciting projects, 
                  let's talk!
                </p>
                
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 glass rounded-full flex items-center justify-center">
                      <span className="text-cyan-400">📧</span>
                    </div>
                    <span className="text-white/70">chrispi.odiwuor@email.com</span>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 glass rounded-full flex items-center justify-center">
                      <span className="text-cyan-400">🌍</span>
                    </div>
                    <span className="text-white/70">Available for remote work</span>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 glass rounded-full flex items-center justify-center">
                      <span className="text-cyan-400">⚡</span>
                    </div>
                    <span className="text-white/70">Quick response time</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Contact form */}
            <div className="glass rounded-2xl p-8 relative overflow-hidden">
              {/* Background cosmic effect */}
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-purple-500/5 to-transparent" />
              
              <form onSubmit={handleSubmit} className="relative z-10 space-y-6">
                <div>
                  <label htmlFor="name" className="block text-white/80 mb-2 text-sm font-medium">
                    Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full px-4 py-3 glass rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50 focus:bg-white/10 transition-all duration-300 outline-none"
                    placeholder="Your name"
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="email" className="block text-white/80 mb-2 text-sm font-medium">
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-4 py-3 glass rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50 focus:bg-white/10 transition-all duration-300 outline-none"
                    placeholder="your.email@example.com"
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="message" className="block text-white/80 mb-2 text-sm font-medium">
                    Message
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    rows={5}
                    className="w-full px-4 py-3 glass rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50 focus:bg-white/10 transition-all duration-300 outline-none resize-none"
                    placeholder="Tell me about your project or just say hi..."
                    required
                  />
                </div>
                
                <Button
                  type="submit"
                  size="lg"
                  className="w-full bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-400/50 text-white hover:from-cyan-500/30 hover:to-purple-500/30 neon-glow"
                >
                  Send Message
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;
