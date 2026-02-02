'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { BarChart3, LogOut, User, Menu } from 'lucide-react';
import { Button } from '@/components/ui';
import { useAuthStore } from '@/stores/auth';

interface HeaderProps {
  onMenuClick?: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const router = useRouter();
  const { user, logout, isAuthenticated } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    router.push('/auth/login');
  };

  return (
    <header className="sticky top-0 z-40 border-b border-neutral-200 bg-white">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-4">
          {onMenuClick && (
            <button
              onClick={onMenuClick}
              className="rounded-lg p-2 hover:bg-neutral-100 lg:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>
          )}
          <Link href="/dashboard" className="flex items-center gap-2">
            <BarChart3 className="h-7 w-7 text-primary-600" />
            <span className="text-lg font-semibold">Sentimatrix Studio</span>
          </Link>
        </div>

        {isAuthenticated && user && (
          <div className="flex items-center gap-4">
            <div className="hidden items-center gap-2 sm:flex">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-primary-600">
                <User className="h-4 w-4" />
              </div>
              <span className="text-sm font-medium">{user.name}</span>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
              <span className="ml-2 hidden sm:inline">Logout</span>
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
