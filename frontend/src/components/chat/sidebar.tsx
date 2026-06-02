"use client";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { useRouter, useParams } from "next/navigation";
import { useChatStore } from "@/store/chat";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Plus,
  MessageSquare,
  Trash2,
  LogOut,
  Settings,
  PanelLeftOpen,
  PanelLeftClose,
  Search,
  PenSquare,
  X,
  Menu,
} from "lucide-react";

export function Sidebar() {
  const router = useRouter();
  const params = useParams();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const closeMobile = () => setMobileOpen(false);

  const { chats, fetchChats, createChat, deleteChat, isLoadingChats } = useChatStore();
  const { user, logout } = useAuthStore();
  const currentChatId = params?.chatId as string;

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  const handleNewChat = async () => {
    const chat = await createChat();
    if (chat) {
      router.push(`/c/${chat.id}`);
    }
  };

  const handleDelete = async (e: React.MouseEvent, chatId: string) => {
    e.stopPropagation();
    if (confirm("Bu sohbet silinsin mi?")) {
      await deleteChat(chatId);
      if (currentChatId === chatId) {
        router.push("/");
      }
    }
  };

  const filteredChats = chats.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleChatClick = (chatId: string) => {
    router.push(`/c/${chatId}`);
    closeMobile();
  };

  return (
    <>
      {typeof window !== "undefined" && mobileOpen && createPortal(
        <div
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          onClick={closeMobile}
        />,
        document.body
      )}
      {typeof window !== "undefined" && !mobileOpen && createPortal(
        <button
          onClick={() => setMobileOpen(true)}
          className="fixed top-3 left-3 z-50 md:hidden flex items-center justify-center h-9 w-9 rounded-lg bg-background border border-border shadow-sm"
          aria-label="Menüyü aç"
        >
          <Menu size={18} />
        </button>,
        document.body
      )}
    <div
      className={cn(
        "flex flex-col h-screen bg-secondary/30 border-r border-border transition-all duration-200",
        collapsed ? "w-14" : "w-72",
        "md:relative fixed z-50 top-0 left-0",
        mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}
    >
      <div className="flex items-center justify-between p-3 border-b border-border">
        {!collapsed && (
          <span className="font-ottoman font-semibold text-lg tracking-wide text-primary">Osmanlı Yapay Zeka</span>
        )}
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={closeMobile}
            className="h-8 w-8 md:hidden"
          >
            <X size={16} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="h-8 w-8"
          >
            {collapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
          </Button>
        </div>
      </div>

      {!collapsed && (
        <div className="p-3">
          <Button
            onClick={handleNewChat}
            className="w-full justify-start gap-2"
            size="sm"
          >
            <PenSquare size={16} />
            Yeni Sohbet
          </Button>
        </div>
      )}

      {collapsed && (
        <div className="p-2">
          <Button
            onClick={handleNewChat}
            variant="ghost"
            size="icon"
            className="w-full h-8"
          >
            <Plus size={16} />
          </Button>
        </div>
      )}

      {!collapsed && (
        <div className="px-3 pb-2">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Sohbet ara..."
              className="w-full h-8 pl-8 pr-3 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto scrollbar-thin px-2">
        {isLoadingChats ? (
          <div className="flex justify-center py-8">
            <div className="flex gap-1">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        ) : filteredChats.length === 0 ? (
          !collapsed && (
            <div className="text-center text-muted-foreground text-sm py-8">
              {searchQuery ? "Sohbet bulunamadı" : "Henüz sohbet yok"}
            </div>
          )
        ) : (
          filteredChats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => handleChatClick(chat.id)}
              className={cn(
                "group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors mb-1",
                currentChatId === chat.id
                  ? "bg-accent/20 text-accent-foreground border border-accent/30"
                  : "hover:bg-secondary text-muted-foreground hover:text-foreground"
              )}
            >
              <MessageSquare size={16} className="shrink-0" />
              {!collapsed && (
                <>
                  <span className="flex-1 truncate text-sm">{chat.title}</span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 opacity-0 group-hover:opacity-100 shrink-0"
                    onClick={(e) => handleDelete(e, chat.id)}
                  >
                    <Trash2 size={12} />
                  </Button>
                </>
              )}
            </div>
          ))
        )}
      </div>

      <div className="border-t border-border p-3">
        {collapsed ? (
          <div className="flex flex-col gap-1">
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => router.push("/settings")}>
              <Settings size={16} />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={logout}>
              <LogOut size={16} />
            </Button>
          </div>
        ) : (
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 flex-1 min-w-0">
              <div className="h-7 w-7 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-primary-foreground text-xs font-medium shrink-0">
                {user?.full_name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || "K"}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.full_name || "Kullanıcı"}</p>
                <p className="text-xs text-muted-foreground capitalize">{user?.role === "admin" ? "Yönetici" : user?.role === "pro" ? "Pro" : "Ücretsiz"}</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => router.push("/settings")}>
              <Settings size={16} />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={logout}>
              <LogOut size={16} />
            </Button>
          </div>
        )}
      </div>
    </div>
    </>
  );
}
