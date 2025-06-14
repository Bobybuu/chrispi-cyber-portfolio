
import { Cloud, Docker, Kubernetes, Github } from "lucide-react";

const SkillsSection = () => {
  const skills = [
    {
      category: "Cloud Platforms",
      skills: [
        { name: "AWS", level: 95, icon: Cloud, color: "from-orange-400 to-orange-600" },
        { name: "Azure", level: 88, icon: Cloud, color: "from-blue-400 to-blue-600" },
        { name: "GCP", level: 82, icon: Cloud, color: "from-green-400 to-green-600" },
      ]
    },
    {
      category: "Containerization",
      skills: [
        { name: "Docker", level: 92, icon: Docker, color: "from-blue-400 to-blue-600" },
        { name: "Kubernetes", level: 89, icon: Kubernetes, color: "from-cyan-400 to-cyan-600" },
        { name: "Helm", level: 85, icon: Kubernetes, color: "from-purple-400 to-purple-600" },
      ]
    },
    {
      category: "CI/CD & Automation",
      skills: [
        { name: "Jenkins", level: 90, icon: Github, color: "from-yellow-400 to-yellow-600" },
        { name: "GitHub Actions", level: 93, icon: Github, color: "from-gray-400 to-gray-600" },
        { name: "Terraform", level: 87, icon: Cloud, color: "from-purple-400 to-purple-600" },
      ]
    },
  ];

  return (
    <section className="py-20 relative">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            Skills & <span className="neon-text">Technologies</span>
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {skills.map((category, categoryIndex) => (
              <div key={categoryIndex} className="glass rounded-2xl p-6 hover:bg-white/15 transition-all duration-300">
                <h3 className="text-xl font-semibold mb-6 text-cyan-400">
                  {category.category}
                </h3>
                
                <div className="space-y-6">
                  {category.skills.map((skill, skillIndex) => (
                    <div key={skillIndex} className="group">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <skill.icon className="w-5 h-5 text-white/70 group-hover:text-cyan-400 transition-colors" />
                          <span className="text-white/90 font-medium">{skill.name}</span>
                        </div>
                        <span className="text-white/60 text-sm">{skill.level}%</span>
                      </div>
                      
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className={`h-full bg-gradient-to-r ${skill.color} rounded-full transition-all duration-1000 ease-out neon-glow`}
                          style={{ width: `${skill.level}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default SkillsSection;
