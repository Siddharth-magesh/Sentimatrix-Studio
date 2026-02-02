import Link from 'next/link';
import { BarChart3 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui';
import { LoginForm } from '@/components/forms';

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-neutral-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100">
            <BarChart3 className="h-6 w-6 text-primary-600" />
          </div>
          <CardTitle>Welcome back</CardTitle>
          <CardDescription>Sign in to your Sentimatrix Studio account</CardDescription>
        </CardHeader>
        <CardContent>
          <LoginForm />
        </CardContent>
        <CardFooter className="justify-center">
          <p className="text-sm text-neutral-600">
            Don&apos;t have an account?{' '}
            <Link href="/auth/register" className="font-medium text-primary-600 hover:text-primary-700">
              Sign up
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
