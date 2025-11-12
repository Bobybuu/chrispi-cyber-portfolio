import { Cloud } from "lucide-react";
import { Button } from "./ui/button";

const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20">
      <div className="container mx-auto px-6 text-center">
        <div className="max-w-4xl mx-auto">
          {/* Avatar/Logo */}
          <div className="mb-8 flex justify-center">
            <div className="relative">
              <div className="w-32 h-32 glass rounded-full flex items-center justify-center neon-glow floating">
                <Cloud className="w-16 h-16 text-cyan-400" />
              </div>
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-400/20 to-purple-400/20 animate-pulse" />
            </div>
          </div>
          
          {/* Main heading */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
            Hi, I'm{" "}
            <span className="neon-text">Chrispin Odiwuor</span>
          </h1>
          
          <div className="text-xl md:text-2xl text-white/80 mb-8 max-w-3xl mx-auto">
            A DevOps Engineer building{" "}
            <span className="text-cyan-400 font-semibold">scalable</span>,{" "}
            <span className="text-purple-400 font-semibold">reliable</span>{" "}
            infrastructure that powers the future.
          </div>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              size="lg"
              className="glass-hover border border-cyan-400/50 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-white hover:from-cyan-500/30 hover:to-purple-500/30 neon-glow px-8 py-3"
            >
              Download Resume
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="glass-hover border border-white/30 text-white hover:border-cyan-400/50 px-8 py-3"
            >
              Contact Me
            </Button>
          </div>
          
          {/* Floating tech icons */}
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-cyan-400 rounded-full animate-pulse opacity-60" />
            <div className="absolute top-1/3 right-1/4 w-1 h-1 bg-purple-400 rounded-full animate-pulse opacity-40 delay-1000" />
            <div className="absolute bottom-1/3 left-1/3 w-3 h-3 bg-cyan-300 rounded-full animate-pulse opacity-30 delay-2000" />
            <div className="absolute bottom-1/4 right-1/3 w-2 h-2 bg-purple-300 rounded-full animate-pulse opacity-50 delay-3000" />
          </div>
        </div>
      </div>
      
      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2">
        <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center">
          <div className="w-1 h-3 bg-gradient-to-b from-cyan-400 to-transparent rounded-full mt-2 animate-bounce" />
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
