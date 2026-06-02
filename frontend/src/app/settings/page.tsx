"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { Subscription } from "@/types";
import { ArrowLeft, Moon, Sun, Loader2 } from "lucide-react";
import { useTheme } from "@/components/layout/theme-provider";

export default function SettingsPage() {
  const router = useRouter();
  const { user, setUser } = useAuthStore();
  const { theme, setTheme } = useTheme();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [saving, setSaving] = useState(false);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loadingSub, setLoadingSub] = useState(true);

  useEffect(() => {
    api.get<Subscription>("/billing/subscription")
      .then(setSubscription)
      .catch(() => {})
      .finally(() => setLoadingSub(false));
  }, []);

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      const updated = await api.patch<{ id: string; email: string; full_name: string }>("/auth/profile", { full_name: fullName });
      if (user) setUser({ ...user, full_name: updated.full_name });
    } catch {}
    setSaving(false);
  };

  const planTitles: Record<string, string> = {
    free: "Ücretsiz",
    pro: "Pro",
    enterprise: "Kurumsal",
    admin: "Yönetici",
  };

  const planColors: Record<string, string> = {
    free: "bg-secondary text-secondary-foreground",
    pro: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    enterprise: "bg-purple-500/10 text-purple-500 border-purple-500/20",
    admin: "bg-amber-500/10 text-amber-500 border-amber-500/20",
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-8">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/")}>
          <ArrowLeft size={20} />
        </Button>
        <div>
          <h1 className="text-2xl font-bold font-ottoman">Ayarlar</h1>
          <p className="text-muted-foreground text-sm">Hesabınızı ve tercihlerinizi yönetin</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="font-ottoman">Profil</CardTitle>
          <CardDescription>Kişisel bilgilerinizi güncelleyin</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">E-posta</label>
            <Input value={user?.email || ""} disabled className="bg-muted/50" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Ad Soyad</label>
            <Input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Adınız"
            />
          </div>
          <Button onClick={handleSaveProfile} disabled={saving}>
            {saving && <Loader2 size={16} className="animate-spin mr-2" />}
            Kaydet
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-ottoman">Abonelik</CardTitle>
          <CardDescription>Planınızı ve faturalandırmayı yönetin</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loadingSub ? (
            <div className="flex gap-1 py-4">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between p-4 rounded-lg bg-secondary/50">
                <div>
                  <p className="font-medium">Mevcut Plan</p>
                  <p className="text-sm text-muted-foreground">
                    {subscription?.plan === "pro" ? "Pro plan - sınırsız mesaj & özellikler" :
                     subscription?.plan === "enterprise" ? "Kurumsal plan" :
                     "Ücretsiz plan - sınırlı mesaj"}
                  </p>
                </div>
                <Badge className={planColors[subscription?.plan || "free"]}>
                  {planTitles[subscription?.plan || "free"]}
                </Badge>
              </div>

              {(!subscription || subscription.plan === "free") && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg border border-border hover:border-accent/50 cursor-pointer transition-colors">
                    <h3 className="font-semibold mb-1 font-ottoman">Ücretsiz</h3>
                    <p className="text-2xl font-bold">₺0</p>
                    <p className="text-xs text-muted-foreground mt-2">Ayda 50 mesaj</p>
                    <p className="text-xs text-muted-foreground">Temel özellikler</p>
                    <Badge variant="secondary" className="mt-3">Mevcut</Badge>
                  </div>
                  <div
                    className="p-4 rounded-lg border border-border hover:border-accent/50 cursor-pointer transition-colors bg-accent/5"
                    onClick={async () => {
                      const res = await api.post<{ url: string }>("/billing/create-checkout", {
                        price_id: "pro",
                        success_url: window.location.href,
                        cancel_url: window.location.href,
                      });
                      if (res.url) window.location.href = res.url;
                    }}
                  >
                    <h3 className="font-semibold mb-1 font-ottoman">Pro</h3>
                    <p className="text-2xl font-bold">$20</p>
                    <p className="text-xs text-muted-foreground mt-2">/ay</p>
                    <p className="text-xs text-muted-foreground">Sınırsız mesaj</p>
                    <p className="text-xs text-muted-foreground">Tüm özellikler</p>
                    <Button size="sm" className="mt-3 w-full">Yükselt</Button>
                  </div>
                </div>
              )}

              {subscription && subscription.plan !== "free" && (
                <Button
                  variant="outline"
                  onClick={async () => {
                    const res = await api.post<{ url: string }>("/billing/create-portal", {
                      return_url: window.location.href,
                    });
                    if (res.url) window.location.href = res.url;
                  }}
                >
                  Faturalandırmayı Yönet
                </Button>
              )}
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-ottoman">Görünüm</CardTitle>
          <CardDescription>Arayüzünüzü özelleştirin</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 rounded-lg bg-secondary/50">
            <div className="flex items-center gap-3">
              {theme === "dark" ? <Moon size={20} /> : <Sun size={20} />}
              <div>
                <p className="font-medium">Tema</p>
                <p className="text-sm text-muted-foreground">
                  {theme === "dark" ? "Karanlık mod" : theme === "light" ? "Aydınlık mod" : "Sistem teması"}
                </p>
              </div>
            </div>
            <div className="flex gap-1">
              {(["light", "dark", "system"] as const).map((t) => (
                <Button
                  key={t}
                  variant={theme === t ? "default" : "ghost"}
                  size="sm"
                  className="text-xs capitalize"
                  onClick={() => setTheme(t)}
                >
                  {t === "light" ? "Aydınlık" : t === "dark" ? "Karanlık" : "Sistem"}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
