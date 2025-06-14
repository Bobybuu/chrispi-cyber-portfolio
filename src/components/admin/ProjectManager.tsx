
import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Card } from "../ui/card";
import { Textarea } from "../ui/textarea";
import { Plus, Edit, Trash2, Save, X } from "lucide-react";
import { useToast } from "../../hooks/use-toast";

interface Project {
  id: string;
  title: string;
  description: string;
  image: string;
  techStack: string[];
  github: string;
  demo: string;
}

const ProjectManager = () => {
  const { toast } = useToast();
  const [projects, setProjects] = useState<Project[]>([
    {
      id: "1",
      title: "Cloud Infrastructure Automation",
      description: "Automated multi-cloud infrastructure deployment using Terraform and Ansible, reducing deployment time by 80% and ensuring consistent environments across dev, staging, and production.",
      image: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=400&fit=crop",
      techStack: ["Terraform", "AWS", "Docker", "Kubernetes"],
      github: "https://github.com",
      demo: "https://demo.com"
    },
    {
      id: "2",
      title: "CI/CD Pipeline Optimization",
      description: "Designed and implemented comprehensive CI/CD pipelines using GitHub Actions, reducing build times by 60% and achieving 99.9% deployment success rate.",
      image: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop",
      techStack: ["GitHub Actions", "Docker", "Kubernetes", "Monitoring"],
      github: "https://github.com",
      demo: "https://demo.com"
    },
    {
      id: "3",
      title: "Microservices Architecture",
      description: "Migrated monolithic applications to microservices architecture on Kubernetes, improving scalability and reducing resource costs by 40%.",
      image: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&h=400&fit=crop",
      techStack: ["Kubernetes", "Docker", "Istio", "Prometheus"],
      github: "https://github.com",
      demo: "https://demo.com"
    }
  ]);

  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  const handleAddProject = (projectData: Omit<Project, 'id'>) => {
    const newProject: Project = {
      ...projectData,
      id: Date.now().toString(),
      techStack: projectData.techStack.filter(tech => tech.trim() !== '')
    };
    setProjects(prev => [...prev, newProject]);
    setShowAddForm(false);
    toast({
      title: "Project Added",
      description: "New project has been added successfully."
    });
  };

  const handleUpdateProject = (updatedProject: Project) => {
    setProjects(prev => prev.map(p => p.id === updatedProject.id ? updatedProject : p));
    setEditingProject(null);
    toast({
      title: "Project Updated",
      description: "Project has been updated successfully."
    });
  };

  const handleDeleteProject = (id: string) => {
    setProjects(prev => prev.filter(p => p.id !== id));
    toast({
      title: "Project Deleted",
      description: "Project has been deleted successfully."
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Manage Projects</h2>
        <Button
          onClick={() => setShowAddForm(true)}
          className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-400/50 text-white hover:from-cyan-500/30 hover:to-purple-500/30"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Project
        </Button>
      </div>

      {/* Add Project Form */}
      {showAddForm && (
        <ProjectForm
          onSubmit={handleAddProject}
          onCancel={() => setShowAddForm(false)}
        />
      )}

      {/* Edit Project Form */}
      {editingProject && (
        <ProjectForm
          project={editingProject}
          onSubmit={handleUpdateProject}
          onCancel={() => setEditingProject(null)}
          isEditing
        />
      )}

      {/* Projects List */}
      <div className="grid gap-6">
        {projects.map((project) => (
          <Card key={project.id} className="p-6 bg-white/5 border-white/10">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-white mb-2">{project.title}</h3>
                <p className="text-white/70 mb-4">{project.description}</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {project.techStack.map((tech, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-400/30 rounded-full text-xs text-cyan-300"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
                <div className="flex space-x-4 text-sm text-white/60">
                  <span>GitHub: {project.github}</span>
                  <span>Demo: {project.demo}</span>
                </div>
              </div>
              <div className="flex space-x-2 ml-4">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setEditingProject(project)}
                  className="border-cyan-400/50 text-cyan-400 hover:bg-cyan-500/10"
                >
                  <Edit className="w-4 h-4" />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleDeleteProject(project.id)}
                  className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

interface ProjectFormProps {
  project?: Project;
  onSubmit: (project: any) => void;
  onCancel: () => void;
  isEditing?: boolean;
}

const ProjectForm = ({ project, onSubmit, onCancel, isEditing = false }: ProjectFormProps) => {
  const [formData, setFormData] = useState({
    title: project?.title || "",
    description: project?.description || "",
    image: project?.image || "",
    techStack: project?.techStack.join(", ") || "",
    github: project?.github || "",
    demo: project?.demo || ""
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const projectData = {
      ...formData,
      techStack: formData.techStack.split(",").map(tech => tech.trim()),
      ...(isEditing ? { id: project!.id } : {})
    };
    onSubmit(projectData);
  };

  return (
    <Card className="p-6 bg-white/5 border-white/10">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-semibold text-white">
          {isEditing ? "Edit Project" : "Add New Project"}
        </h3>
        <Button
          variant="outline"
          onClick={onCancel}
          className="border-white/30 text-white/70 hover:bg-white/10"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="title" className="text-white/80">Title</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              className="bg-white/5 border-white/20 text-white placeholder-white/50"
              required
            />
          </div>
          <div>
            <Label htmlFor="image" className="text-white/80">Image URL</Label>
            <Input
              id="image"
              value={formData.image}
              onChange={(e) => setFormData(prev => ({ ...prev, image: e.target.value }))}
              className="bg-white/5 border-white/20 text-white placeholder-white/50"
              required
            />
          </div>
        </div>

        <div>
          <Label htmlFor="description" className="text-white/80">Description</Label>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            className="bg-white/5 border-white/20 text-white placeholder-white/50"
            rows={3}
            required
          />
        </div>

        <div>
          <Label htmlFor="techStack" className="text-white/80">Tech Stack (comma separated)</Label>
          <Input
            id="techStack"
            value={formData.techStack}
            onChange={(e) => setFormData(prev => ({ ...prev, techStack: e.target.value }))}
            className="bg-white/5 border-white/20 text-white placeholder-white/50"
            placeholder="React, TypeScript, Node.js"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="github" className="text-white/80">GitHub URL</Label>
            <Input
              id="github"
              value={formData.github}
              onChange={(e) => setFormData(prev => ({ ...prev, github: e.target.value }))}
              className="bg-white/5 border-white/20 text-white placeholder-white/50"
              required
            />
          </div>
          <div>
            <Label htmlFor="demo" className="text-white/80">Demo URL</Label>
            <Input
              id="demo"
              value={formData.demo}
              onChange={(e) => setFormData(prev => ({ ...prev, demo: e.target.value }))}
              className="bg-white/5 border-white/20 text-white placeholder-white/50"
              required
            />
          </div>
        </div>

        <div className="flex space-x-4 pt-4">
          <Button
            type="submit"
            className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-400/50 text-white hover:from-cyan-500/30 hover:to-purple-500/30"
          >
            <Save className="w-4 h-4 mr-2" />
            {isEditing ? "Update Project" : "Add Project"}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            className="border-white/30 text-white/70 hover:bg-white/10"
          >
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default ProjectManager;
