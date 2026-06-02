"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import {
  Users, MessageSquare, FileText, CreditCard, Activity,
  TrendingUp, AlertTriangle, ArrowLeft
} from "lucide-react";

export default function AdminPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user && user.role !== "admin") {
      router.push("/");
      return;
    }
    loadData();
  }, [user]);

  const loadData = async () => {
    try {
      const [statsData, usersData, analyticsData] = await Promise.all([
        api.get<any>("/admin/dashboard"),
        api.get<any>("/admin/users?page=1&per_page=10"),
        api.get<any>("/admin/analytics"),
      ]);
      setStats(statsData);
      setUsers(usersData.users || []);
      setAnalytics(analyticsData);
    } catch {}
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="flex gap-1">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      </div>
    );
  }

  const statCards = [
    { title: "Toplam Kullanıcı", value: stats?.users_count || 0, icon: Users, color: "text-blue-500" },
    { title: "Toplam Sohbet", value: stats?.chats_count || 0, icon: MessageSquare, color: "text-green-500" },
    { title: "Toplam Mesaj", value: stats?.messages_count || 0, icon: Activity, color: "text-purple-500" },
    { title: "Belgeler", value: stats?.documents_count || 0, icon: FileText, color: "text-amber-500" },
    { title: "Aktif Abonelik", value: stats?.active_subscriptions || 0, icon: CreditCard, color: "text-emerald-500" },
    { title: "Gelir (30g)", value: `$${stats?.revenue_monthly?.toFixed(0) || "0"}`, icon: TrendingUp, color: "text-rose-500" },
    { title: "API İstek (Bugün)", value: stats?.api_requests_today || 0, icon: Activity, color: "text-cyan-500" },
    { title: "Hata Oranı", value: `${stats?.error_rate || 0}%`, icon: AlertTriangle, color: "text-red-500" },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push("/")}>
            <ArrowLeft size={20} />
          </Button>
          <div>
            <h1 className="text-2xl font-bold font-ottoman">Yönetim Paneli</h1>
            <p className="text-muted-foreground text-sm">Osmanlı Yapay Zeka platformunu yönetin</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <Card key={stat.title}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.title}</p>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                </div>
                <stat.icon className={`h-8 w-8 ${stat.color} opacity-60`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-ottoman">Analitik</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-border">
                <span className="text-sm text-muted-foreground">Toplam Kullanıcı</span>
                <span className="font-medium">{analytics?.total_users || 0}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border">
                <span className="text-sm text-muted-foreground">Aktif (Bugün)</span>
                <span className="font-medium">{analytics?.active_users_today || 0}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border">
                <span className="text-sm text-muted-foreground">Toplam Mesaj</span>
                <span className="font-medium">{analytics?.total_messages || 0}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border">
                <span className="text-sm text-muted-foreground">Toplam Token</span>
                <span className="font-medium">{(analytics?.total_tokens || 0).toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-sm text-muted-foreground">Toplam Gelir</span>
                <span className="font-medium">${(analytics?.total_revenue || 0).toFixed(2)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-ottoman">Son Kullanıcılar</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {users.slice(0, 5).map((u: any) => (
                <div key={u.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                  <div>
                    <p className="text-sm font-medium">{u.full_name || u.email}</p>
                    <p className="text-xs text-muted-foreground">{u.email}</p>
                  </div>
                  <span className="text-xs capitalize px-2 py-1 rounded bg-secondary">
                    {u.role === "admin" ? "Yönetici" : u.role === "pro" ? "Pro" : "Ücretsiz"}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
