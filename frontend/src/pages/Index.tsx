import { useState, useEffect } from "react";
import { User } from "@/types";
import AuthPage from "@/components/AuthPage";
import Dashboard from "@/components/Dashboard";

const STORAGE_KEY = "apc_user";

const Index = () => {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    if (user) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [user]);

  const handleLogin = (userData: User) => setUser(userData);
  const handleLogout = () => setUser(null);

  if (!user) return <AuthPage onLogin={handleLogin} />;
  return <Dashboard user={user} onLogout={handleLogout} />;
};

export default Index;
