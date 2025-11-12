
import { Cloud, Github, Linkedin, Twitter, Mail, MapPin, ArrowUp } from "lucide-react";
import { Button } from "./ui/button";

const Footer = () => {
  const navItems = [
    { id: "hero", label: "Home" },
    { id: "about", label: "About" },
    { id: "projects", label: "Projects" },
    { id: "contact", label: "Contact" },
  ];

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer className="relative bg-slate-900/50 border-t border-white/10">
      {/* Main Footer Content */}
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand & Quote Section */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Cloud className="w-8 h-8 text-cyan-400" />
              <span className="text-xl font-bold neon-text">Chrispin Odiwuor</span>
            </div>
            <p className="text-white/60 text-sm">
              DevOps Engineer & Innovator
            </p>
            <p className="text-cyan-400/80 italic text-sm">
              "Solving complex problems through simple, innovative code."
            </p>
          </div>

          {/* Navigation & Contact */}
          <div className="space-y-6">
            {/* Quick Links */}
            <div>
              <h3 className="text-white font-semibold mb-3">Quick Links</h3>
              <div className="flex flex-wrap gap-4">
                {navItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToSection(item.id)}
                    className="text-white/60 hover:text-cyan-400 transition-colors text-sm"
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Contact Info */}
            <div>
              <h3 className="text-white font-semibold mb-3">Contact</h3>
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-white/60 text-sm">
                  <MapPin className="w-4 h-4" />
                  <span>Nairobi, Kenya</span>
                </div>
                <div className="flex items-center space-x-2 text-white/60 text-sm">
                  <Mail className="w-4 h-4" />
                  <a href="mailto:chrispin@youremail.com" className="hover:text-cyan-400 transition-colors">
                    chrispin@youremail.com
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* CTA & Social */}
          <div className="space-y-6">
            {/* Call to Action */}
            <div>
              <h3 className="text-white font-semibold mb-3">Let's Collaborate</h3>
              <p className="text-white/60 text-sm mb-4">
                Ready to build something amazing together?
              </p>
              <Button
                size="sm"
                className="glass-hover border border-cyan-400/50 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-white hover:from-cyan-500/30 hover:to-purple-500/30"
                onClick={() => scrollToSection("contact")}
              >
                Get In Touch
              </Button>
            </div>

            {/* Social Links */}
            <div>
              <h3 className="text-white font-semibold mb-3">Follow Me</h3>
              <div className="flex space-x-4">
                <a
                  href="https://github.com"
                  className="p-2 glass-hover rounded-full group"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="GitHub"
                >
                  <Github className="w-5 h-5 text-white/60 group-hover:text-cyan-400 transition-colors" />
                </a>
                <a
                  href="https://linkedin.com"
                  className="p-2 glass-hover rounded-full group"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="LinkedIn"
                >
                  <Linkedin className="w-5 h-5 text-white/60 group-hover:text-cyan-400 transition-colors" />
                </a>
                <a
                  href="https://twitter.com"
                  className="p-2 glass-hover rounded-full group"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Twitter"
                >
                  <Twitter className="w-5 h-5 text-white/60 group-hover:text-cyan-400 transition-colors" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-white/10 py-6">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            {/* Copyright */}
            <p className="text-white/50 text-sm">
              © 2025 Chrispin Odiwuor. All rights reserved.
            </p>

            {/* Back to Top */}
            <button
              onClick={scrollToTop}
              className="flex items-center space-x-2 text-white/60 hover:text-cyan-400 transition-colors group"
              aria-label="Back to top"
            >
              <span className="text-sm">Back to Top</span>
              <ArrowUp className="w-4 h-4 group-hover:transform group-hover:-translate-y-1 transition-transform" />
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
