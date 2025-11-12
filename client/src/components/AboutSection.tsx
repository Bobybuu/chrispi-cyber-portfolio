
import { Cloud, Container, Layers, Github } from "lucide-react";

const AboutSection = () => {
  const techIcons = [
    { Icon: Cloud, label: "AWS", color: "text-orange-400" },
    { Icon: Container, label: "Docker", color: "text-blue-400" },
    { Icon: Layers, label: "Kubernetes", color: "text-cyan-400" },
    { Icon: Cloud, label: "GCP", color: "text-green-400" },
    { Icon: Cloud, label: "Azure", color: "text-blue-500" },
    { Icon: Github, label: "CI/CD", color: "text-purple-400" },
  ];

  return (
    <section className="py-20 relative">
      <div className="container mx-auto px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            About <span className="neon-text">Me</span>
          </h2>
          
          <div className="glass rounded-2xl p-8 md:p-12 relative overflow-hidden">
            {/* Background particles */}
            <div className="absolute inset-0 overflow-hidden">
              {[...Array(20)].map((_, i) => (
                <div
                  key={i}
                  className="absolute w-1 h-1 bg-cyan-400/20 rounded-full animate-pulse"
                  style={{
                    left: `${Math.random() * 100}%`,
                    top: `${Math.random() * 100}%`,
                    animationDelay: `${Math.random() * 3}s`,
                  }}
                />
              ))}
            </div>
            
            <div className="relative z-10">
              <div className="text-lg md:text-xl text-white/80 leading-relaxed mb-8">
                I'm passionate about building robust, automated infrastructure that scales with business needs. 
                With expertise in cloud platforms, containerization, and CI/CD pipelines, I transform complex 
                deployment challenges into elegant, automated solutions.
              </div>
              
              <div className="text-white/70 mb-8">
                My journey in DevOps is driven by a love for automation, infrastructure as code, and fostering 
                a collaborative culture between development and operations teams. I believe in the power of 
                continuous integration, monitoring, and iterative improvement to deliver exceptional software experiences.
              </div>
              
              {/* Tech stack icons */}
              <div className="grid grid-cols-3 md:grid-cols-6 gap-6">
                {techIcons.map((tech, index) => (
                  <div
                    key={index}
                    className="flex flex-col items-center p-4 glass-hover rounded-xl group cursor-pointer"
                  >
                    <tech.Icon className={`w-8 h-8 ${tech.color} group-hover:scale-110 transition-transform duration-300`} />
                    <span className="text-xs text-white/60 mt-2 group-hover:text-white/80 transition-colors">
                      {tech.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;
