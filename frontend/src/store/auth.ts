"use client";
import { create } from "zustand";
import { User } from "@/types";
import { api, setToken, getToken } from "@/lib/api";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, full_name?: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    const data = await api.post<{
      access_token: string;
      refresh_token: string;
      user: User;
    }>("/auth/login", { email, password });
    setToken(data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    set({ user: data.user, isAuthenticated: true, isLoading: false });
  },

  signup: async (email: string, password: string, full_name?: string) => {
    const data = await api.post<{
      access_token: string;
      refresh_token: string;
      user: User;
    }>("/auth/signup", { email, password, full_name });
    setToken(data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    set({ user: data.user, isAuthenticated: true, isLoading: false });
  },

  logout: () => {
    setToken(null);
    localStorage.removeItem("refresh_token");
    set({ user: null, isAuthenticated: false, isLoading: false });
  },

  fetchUser: async () => {
    const token = getToken();
    if (!token) {
      set({ isLoading: false, isAuthenticated: false });
      return;
    }
    try {
      const user = await api.get<User>("/auth/me");
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      setToken(null);
      localStorage.removeItem("refresh_token");
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  setUser: (user: User) => set({ user }),
}));
