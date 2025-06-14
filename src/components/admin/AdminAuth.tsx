
import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Card } from "../ui/card";
import { Lock, User } from "lucide-react";

interface AdminAuthProps {
  onAuthenticated: () => void;
}

const AdminAuth = ({ onAuthenticated }: AdminAuthProps) => {
  const [credentials, setCredentials] = useState({
    username: "",
    password: ""
  });
  const [error, setError] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Simple authentication - in a real app, this would be handled by a backend
    if (credentials.username === "admin" && credentials.password === "admin123") {
      onAuthenticated();
    } else {
      setError("Invalid credentials. Use admin/admin123");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
      <Card className="w-full max-w-md p-8 bg-white/5 border-white/10 backdrop-blur-lg">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-cyan-400/30">
            <Lock className="w-8 h-8 text-cyan-400" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Admin Login</h1>
          <p className="text-white/60">Access the portfolio dashboard</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <Label htmlFor="username" className="text-white/80">Username</Label>
            <div className="relative mt-2">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/50" />
              <Input
                id="username"
                type="text"
                value={credentials.username}
                onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
                className="pl-10 bg-white/5 border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50"
                placeholder="Enter username"
                required
              />
            </div>
          </div>

          <div>
            <Label htmlFor="password" className="text-white/80">Password</Label>
            <div className="relative mt-2">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/50" />
              <Input
                id="password"
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
                className="pl-10 bg-white/5 border-white/20 text-white placeholder-white/50 focus:border-cyan-400/50"
                placeholder="Enter password"
                required
              />
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-500/20 border border-red-400/30 rounded-lg">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-400/50 text-white hover:from-cyan-500/30 hover:to-purple-500/30"
          >
            Login
          </Button>
        </form>

        <div className="mt-6 p-4 bg-cyan-500/10 border border-cyan-400/30 rounded-lg">
          <p className="text-cyan-400 text-sm font-medium mb-1">Demo Credentials:</p>
          <p className="text-white/70 text-sm">Username: admin</p>
          <p className="text-white/70 text-sm">Password: admin123</p>
        </div>
      </Card>
    </div>
  );
};

export default AdminAuth;
