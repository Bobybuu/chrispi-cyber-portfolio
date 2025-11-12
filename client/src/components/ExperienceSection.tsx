
import { Cloud } from "lucide-react";

const ExperienceSection = () => {
  const experiences = [
    {
      title: "Senior DevOps Engineer",
      company: "TechCorp Solutions",
      period: "2022 - Present",
      description: "Leading cloud infrastructure initiatives and mentoring junior engineers. Implemented automated deployment pipelines that reduced deployment time by 75%.",
      achievements: [
        "Migrated legacy systems to cloud-native architecture",
        "Established monitoring and alerting systems",
        "Reduced infrastructure costs by 40%"
      ]
    },
    {
      title: "DevOps Engineer",
      company: "InnovateTech",
      period: "2020 - 2022",
      description: "Built and maintained CI/CD pipelines for multiple microservices. Collaborated with development teams to improve deployment reliability.",
      achievements: [
        "Achieved 99.9% uptime across all services",
        "Implemented Infrastructure as Code practices",
        "Automated testing and deployment processes"
      ]
    },
    {
      title: "Junior DevOps Engineer",
      company: "StartupHub",
      period: "2019 - 2020",
      description: "Started my DevOps journey by learning containerization and cloud platforms. Contributed to system monitoring and maintenance.",
      achievements: [
        "Containerized 15+ applications using Docker",
        "Set up monitoring dashboards",
        "Optimized CI/CD workflows"
      ]
    }
  ];

  return (
    <section className="py-20 relative">
      <div className="container mx-auto px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            Work <span className="neon-text">Experience</span>
          </h2>
          
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-cyan-400 via-purple-400 to-cyan-400 rounded-full" />
            
            <div className="space-y-12">
              {experiences.map((exp, index) => (
                <div key={index} className="relative flex items-start space-x-8">
                  {/* Timeline dot */}
                  <div className="relative z-10">
                    <div className="w-16 h-16 glass rounded-full flex items-center justify-center neon-glow">
                      <Cloud className="w-8 h-8 text-cyan-400" />
                    </div>
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 glass rounded-2xl p-6 hover:bg-white/15 transition-all duration-300">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-white mb-1">
                          {exp.title}
                        </h3>
                        <p className="text-cyan-400 font-medium">{exp.company}</p>
                      </div>
                      <span className="text-white/60 text-sm mt-2 md:mt-0">
                        {exp.period}
                      </span>
                    </div>
                    
                    <p className="text-white/80 mb-4 leading-relaxed">
                      {exp.description}
                    </p>
                    
                    <ul className="space-y-2">
                      {exp.achievements.map((achievement, achIndex) => (
                        <li key={achIndex} className="flex items-start text-white/70 text-sm">
                          <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full mt-2 mr-3 flex-shrink-0" />
                          {achievement}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ExperienceSection;
