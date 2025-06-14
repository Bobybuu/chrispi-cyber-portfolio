import { Cloud, Github, Linkedin, Twitter } from "lucide-react";

interface NavigationProps {
  activeSection: string;
}

const Navigation = ({ activeSection }: NavigationProps) => {
  const navItems = [
    { id: "hero", label: "Home" },
    { id: "about", label: "About" },
    { id: "skills", label: "Skills" },
    { id: "projects", label: "Projects" },
    { id: "experience", label: "Experience" },
    { id: "contact", label: "Contact" },
  ];

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Cloud className="w-8 h-8 text-cyan-400" />
            <span className="text-xl font-bold neon-text">Chrispin Odiwuor</span>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => scrollToSection(item.id)}
                className={`relative px-3 py-2 text-sm font-medium transition-all duration-300 ${
                  activeSection === item.id
                    ? "text-cyan-400"
                    : "text-white/70 hover:text-white"
                }`}
              >
                {item.label}
                {activeSection === item.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-400 to-purple-400 rounded-full" />
                )}
              </button>
            ))}
          </div>
          
          <div className="flex items-center space-x-4">
            <a
              href="https://github.com"
              className="p-2 glass-hover rounded-full"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github className="w-5 h-5 text-white/70 hover:text-cyan-400 transition-colors" />
            </a>
            <a
              href="https://linkedin.com"
              className="p-2 glass-hover rounded-full"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Linkedin className="w-5 h-5 text-white/70 hover:text-cyan-400 transition-colors" />
            </a>
            <a
              href="https://twitter.com"
              className="p-2 glass-hover rounded-full"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Twitter className="w-5 h-5 text-white/70 hover:text-cyan-400 transition-colors" />
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
