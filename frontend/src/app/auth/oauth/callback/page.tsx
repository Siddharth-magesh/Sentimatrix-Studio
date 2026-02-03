'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Card,
  CardContent,
  CardFooter,
  Button,
  Alert,
} from '@/components/ui';
import { api } from '@/lib/api';
import { useAuthStore } from '@/stores/auth';
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

function OAuthCallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { setAuth } = useAuthStore();

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState<string | null>(null);
  const [provider, setProvider] = useState<string>('OAuth');

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const errorParam = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');
      const providerParam = searchParams.get('provider') || 'oauth';

      setProvider(providerParam.charAt(0).toUpperCase() + providerParam.slice(1));

      // Handle OAuth provider errors
      if (errorParam) {
        setStatus('error');
        setError(errorDescription || `Authentication was denied or cancelled.`);
        return;
      }

      // Validate required parameters
      if (!code) {
        setStatus('error');
        setError('Missing authorization code. Please try again.');
        return;
      }

      try {
        // Exchange code for tokens
        const response = await api.auth.oauthCallback(providerParam, code, state || undefined);

        // Store authentication data
        setAuth(response.access_token, response.user);

        setStatus('success');

        // Redirect to dashboard after short delay
        setTimeout(() => {
          router.push('/dashboard');
        }, 1500);
      } catch (err: any) {
        setStatus('error');
        const errorMessage = err.response?.data?.detail || 'Authentication failed. Please try again.';
        setError(errorMessage);
      }
    };

    handleCallback();
  }, [searchParams, router, setAuth]);

  // Loading state
  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50 px-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center">
              <Loader2 className="h-8 w-8 text-primary-600 animate-spin" />
            </div>
            <h2 className="text-xl font-semibold text-neutral-900">Signing you in...</h2>
            <p className="mt-2 text-sm text-neutral-500">
              Completing {provider} authentication
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Success state
  if (status === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50 px-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-success-100">
              <CheckCircle className="h-6 w-6 text-success-600" />
            </div>
            <h2 className="text-xl font-semibold text-neutral-900">Welcome!</h2>
            <p className="mt-2 text-sm text-neutral-500">
              Successfully signed in with {provider}. Redirecting to dashboard...
            </p>
            <div className="mt-4">
              <div className="h-1 w-full bg-neutral-200 rounded-full overflow-hidden">
                <div className="h-full bg-primary-600 animate-pulse" style={{ width: '100%' }} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Error state
  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50 px-4">
      <Card className="w-full max-w-md">
        <CardContent className="pt-6 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-error-100">
            <AlertCircle className="h-6 w-6 text-error-600" />
          </div>
          <h2 className="text-xl font-semibold text-neutral-900">Authentication Failed</h2>
          <p className="mt-2 text-sm text-neutral-500">
            {error}
          </p>
          {error?.includes('account') && (
            <Alert variant="info" className="mt-4 text-left">
              If you already have an account with a different sign-in method, you can link your
              {provider} account from your account settings after signing in.
            </Alert>
          )}
        </CardContent>
        <CardFooter className="flex justify-center gap-3">
          <Link href="/auth/login">
            <Button variant="outline">Back to Sign In</Button>
          </Link>
          <Link href="/auth/register">
            <Button>Create Account</Button>
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}

export default function OAuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-neutral-50 px-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center">
              <Loader2 className="h-8 w-8 text-primary-600 animate-spin" />
            </div>
            <h2 className="text-xl font-semibold text-neutral-900">Processing...</h2>
            <p className="mt-2 text-sm text-neutral-500">
              Please wait while we complete your sign in
            </p>
          </CardContent>
        </Card>
      </div>
    }>
      <OAuthCallbackContent />
    </Suspense>
  );
}
