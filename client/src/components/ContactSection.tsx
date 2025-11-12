// client/src/components/ContactSection.tsx
import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { useToast } from "../hooks/use-toast";
import { contactAPI } from "../services/api";

interface ContactConfig {
  is_enabled: boolean;
  required_fields: {
    name: boolean;
    email: boolean;
    phone: boolean;
    company: boolean;
    subject: boolean;
  };
  categories: string[];
  recaptcha_enabled: boolean;
  recaptcha_site_key: string;
}

const ContactSection = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    company: "",
    subject: "",
    message: "",
    category: "general",
    consent_given: true,
    newsletter_subscribed: false,
  });
  
  const [config, setConfig] = useState<ContactConfig | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [configLoading, setConfigLoading] = useState(true);
  const { toast } = useToast();

  // Fetch contact form configuration
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const configData = await contactAPI.getConfig();
        setConfig(configData);
      } catch (error) {
        console.error('Failed to load contact form configuration:', error);
        toast({
          title: "Configuration Error",
          description: "Failed to load contact form. Please refresh the page.",
          variant: "destructive",
        });
      } finally {
        setConfigLoading(false);
      }
    };

    fetchConfig();
  }, [toast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!config?.is_enabled) {
      toast({
        title: "Contact form disabled",
        description: "The contact form is currently unavailable. Please try again later.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      // Validate required fields based on config
      if (config.required_fields.name && !formData.name.trim()) {
        throw new Error("Name is required");
      }
      if (config.required_fields.email && !formData.email.trim()) {
        throw new Error("Email is required");
      }
      if (config.required_fields.subject && !formData.subject.trim()) {
        throw new Error("Subject is required");
      }
      if (!formData.message.trim()) {
        throw new Error("Message is required");
      }
      if (!formData.consent_given) {
        throw new Error("Consent is required to process your message");
      }

      const result = await contactAPI.sendMessage(formData);
      
      toast({
        title: "Message sent successfully!",
        description: "Thanks for reaching out. I'll get back to you soon.",
      });
      
      // Reset form
      setFormData({
        name: "",
        email: "",
        phone: "",
        company: "",
        subject: "",
        message: "",
        category: "general",
        consent_given: true,
        newsletter_subscribed: false,
      });

    } catch (error: any) {
      console.error('Failed to send message:', error);
      
      let errorMessage = "Failed to send message. Please try again.";
      
      if (error.code === 'RATE_LIMITED') {
        errorMessage = "Too many contact attempts. Please try again later.";
      } else if (error.code === 'FORM_DISABLED') {
        errorMessage = "Contact form is currently disabled. Please try again later.";
      } else if (error.message) {
        errorMessage = error.message;
      } else if (error.details) {
        // Handle validation errors from backend
        const firstError = Object.values(error.details)[0];
        errorMessage = Array.isArray(firstError) ? firstError[0] : String(firstError);
      }

      toast({
        title: "Error sending message",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({
        ...prev,
        [name]: checked
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  if (configLoading) {
    return (
      <section className="py-20 relative">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="glass rounded-2xl p-8">
              <p className="text-white/80">Loading contact form...</p>
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (!config?.is_enabled) {
    return (
      <section className="py-20 relative">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="glass rounded-2xl p-8">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Contact <span className="neon-text">Unavailable</span>
              </h2>
              <p className="text-white/80">
                The contact form is currently undergoing maintenance. Please check back later or reach out directly via email.
              </p>
            </div>
          </div>
        </div>
      </section>
    );
  }

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
              
              <form onSubmit={handleSubmit} className="relative z-10 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="name" className="block text-white/80 mb-2 text-sm font-medium">
                      Name {config.required_fields.name && <span className="text-red-400">*</span>}
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      className="w-full px-4 py-3 glass rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50 focus:bg-white/10 transition-all duration-300 outline-none"
                      placeholder="Your name"
                      required={config.required_fields.name}
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="email" className="block text-white/80 mb-2 text-sm font-medium">
                      Email {config.required_fields.email && <span className="text-red-400">*</span>}
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full px-4 py-3 glass rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50 focus:bg-white/10 transition-all duration-300 outline-none"
                      placeholder="your.email@example.com"
                      required={config.required_fields.email}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {config.required_fields.phone && (
                    <div>
                      <label htmlFor="phone" className="block text-white/80 mb-2 text-sm font-medium">
                        Phone
                      </label>
                      <input
                        type="tel"
                        id="phone"
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        className="w-full px-4 py-3 glass rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50 focus:bg-white/10 transition-all duration-300 outline-none"
                        placeholder="Your phone number"
                      />
                    </div>
                  )}
                  
                  {config.required_fields.company && (
                    <div>
                      <label htmlFor="company" className="block text-white/80 mb-2 text-sm font-medium">
                        Company
                      </label>
                      <input
                        type="text"
                        id="company"
                        name="company"
                        value={formData.company}
                        onChange={handleChange}
                        className="w-full px-4 py-3 glass rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50 focus:bg-white/10 transition-all duration-300 outline-none"
                        placeholder="Your company"
                      />
                    </div>
                  )}
                </div>

                {config.required_fields.subject && (
                  <div>
                    <label htmlFor="subject" className="block text-white/80 mb-2 text-sm font-medium">
                      Subject
                    </label>
                    <input
                      type="text"
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      className="w-full px-4 py-3 glass rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50 focus:bg-white/10 transition-all duration-300 outline-none"
                      placeholder="Message subject"
                    />
                  </div>
                )}

                {config.categories.length > 0 && (
                  <div>
                    <label htmlFor="category" className="block text-white/80 mb-2 text-sm font-medium">
                      Category
                    </label>
                    <select
                      id="category"
                      name="category"
                      value={formData.category}
                      onChange={handleChange}
                      className="w-full px-4 py-3 glass rounded-lg bg-white/5 border border-white/20 text-white focus:border-cyan-400/50 focus:bg-white/10 transition-all duration-300 outline-none"
                    >
                      {config.categories.map(category => (
                        <option key={category} value={category}>
                          {category.charAt(0).toUpperCase() + category.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
                
                <div>
                  <label htmlFor="message" className="block text-white/80 mb-2 text-sm font-medium">
                    Message <span className="text-red-400">*</span>
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    rows={4}
                    className="w-full px-4 py-3 glass rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50 focus:bg-white/10 transition-all duration-300 outline-none resize-none"
                    placeholder="Tell me about your project or just say hi..."
                    required
                  />
                </div>

                <div className="space-y-3">
                  <label className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      name="consent_given"
                      checked={formData.consent_given}
                      onChange={handleChange}
                      className="w-4 h-4 text-cyan-400 bg-white/5 border-white/20 rounded focus:ring-cyan-400 focus:ring-2"
                      required
                    />
                    <span className="text-white/80 text-sm">
                      I consent to having my data processed according to the privacy policy
                    </span>
                  </label>

                  <label className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      name="newsletter_subscribed"
                      checked={formData.newsletter_subscribed}
                      onChange={handleChange}
                      className="w-4 h-4 text-cyan-400 bg-white/5 border-white/20 rounded focus:ring-cyan-400 focus:ring-2"
                    />
                    <span className="text-white/80 text-sm">
                      Subscribe to newsletter (optional)
                    </span>
                  </label>
                </div>
                
                <Button
                  type="submit"
                  size="lg"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-400/50 text-white hover:from-cyan-500/30 hover:to-purple-500/30 neon-glow disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? "Sending..." : "Send Message"}
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
