import Link from 'next/link';
import { BarChart3 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui';
import { RegisterForm } from '@/components/forms';

export default function RegisterPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-neutral-50 px-4 py-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100">
            <BarChart3 className="h-6 w-6 text-primary-600" />
          </div>
          <CardTitle>Create an account</CardTitle>
          <CardDescription>Get started with Sentimatrix Studio</CardDescription>
        </CardHeader>
        <CardContent>
          <RegisterForm />
        </CardContent>
        <CardFooter className="justify-center">
          <p className="text-sm text-neutral-600">
            Already have an account?{' '}
            <Link href="/auth/login" className="font-medium text-primary-600 hover:text-primary-700">
              Sign in
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
