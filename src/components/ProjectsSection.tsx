
import { Github, Cloud } from "lucide-react";
import { Button } from "./ui/button";

const ProjectsSection = () => {
  const projects = [
    {
      title: "Cloud Infrastructure Automation",
      description: "Automated multi-cloud infrastructure deployment using Terraform and Ansible, reducing deployment time by 80% and ensuring consistent environments across dev, staging, and production.",
      image: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=400&fit=crop",
      techStack: ["Terraform", "AWS", "Docker", "Kubernetes"],
      github: "https://github.com",
      demo: "https://demo.com",
    },
    {
      title: "CI/CD Pipeline Optimization",
      description: "Designed and implemented comprehensive CI/CD pipelines using GitHub Actions, reducing build times by 60% and achieving 99.9% deployment success rate.",
      image: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop",
      techStack: ["GitHub Actions", "Docker", "Kubernetes", "Monitoring"],
      github: "https://github.com",
      demo: "https://demo.com",
    },
    {
      title: "Microservices Architecture",
      description: "Migrated monolithic applications to microservices architecture on Kubernetes, improving scalability and reducing resource costs by 40%.",
      image: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&h=400&fit=crop",
      techStack: ["Kubernetes", "Docker", "Istio", "Prometheus"],
      github: "https://github.com",
      demo: "https://demo.com",
    },
  ];

  return (
    <section className="py-20 relative">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            Featured <span className="neon-text">Projects</span>
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {projects.map((project, index) => (
              <div
                key={index}
                className="glass rounded-2xl overflow-hidden hover:bg-white/15 transition-all duration-300 group"
              >
                <div className="relative overflow-hidden">
                  <img
                    src={project.image}
                    alt={project.title}
                    className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                </div>
                
                <div className="p-6">
                  <h3 className="text-xl font-semibold mb-3 text-white group-hover:text-cyan-400 transition-colors">
                    {project.title}
                  </h3>
                  
                  <p className="text-white/70 text-sm mb-4 leading-relaxed">
                    {project.description}
                  </p>
                  
                  <div className="flex flex-wrap gap-2 mb-4">
                    {project.techStack.map((tech, techIndex) => (
                      <span
                        key={techIndex}
                        className="px-3 py-1 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-400/30 rounded-full text-xs text-cyan-300"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex space-x-3">
                    <Button
                      size="sm"
                      variant="outline"
                      className="glass-hover border-white/30 text-white hover:border-cyan-400/50 flex-1"
                    >
                      <Github className="w-4 h-4 mr-2" />
                      Code
                    </Button>
                    <Button
                      size="sm"
                      className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-400/50 text-white hover:from-cyan-500/30 hover:to-purple-500/30 flex-1"
                    >
                      <Cloud className="w-4 h-4 mr-2" />
                      Demo
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProjectsSection;
