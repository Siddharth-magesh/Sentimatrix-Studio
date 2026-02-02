'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Input, Label, Alert } from '@/components/ui';
import { useAuthStore } from '@/stores/auth';

const registerSchema = z
  .object({
    name: z.string().min(1, 'Name is required').max(100, 'Name is too long'),
    email: z.string().email('Please enter a valid email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one digit'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const router = useRouter();
  const { register: registerUser, isLoading, error, clearError } = useAuthStore();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setSubmitError(null);
    clearError();

    try {
      await registerUser({
        email: data.email,
        name: data.name,
        password: data.password,
      });
      router.push('/dashboard');
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Registration failed');
    }
  };

  const displayError = submitError || error;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {displayError && (
        <Alert variant="error">{displayError}</Alert>
      )}

      <div className="space-y-2">
        <Label htmlFor="name" required>
          Name
        </Label>
        <Input
          id="name"
          type="text"
          placeholder="John Doe"
          error={errors.name?.message}
          {...register('name')}
        />
        {errors.name && (
          <p className="text-sm text-error-600">{errors.name.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="email" required>
          Email
        </Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          error={errors.email?.message}
          {...register('email')}
        />
        {errors.email && (
          <p className="text-sm text-error-600">{errors.email.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="password" required>
          Password
        </Label>
        <Input
          id="password"
          type="password"
          placeholder="Create a strong password"
          error={errors.password?.message}
          {...register('password')}
        />
        {errors.password && (
          <p className="text-sm text-error-600">{errors.password.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="confirmPassword" required>
          Confirm Password
        </Label>
        <Input
          id="confirmPassword"
          type="password"
          placeholder="Confirm your password"
          error={errors.confirmPassword?.message}
          {...register('confirmPassword')}
        />
        {errors.confirmPassword && (
          <p className="text-sm text-error-600">{errors.confirmPassword.message}</p>
        )}
      </div>

      <Button type="submit" className="w-full" isLoading={isLoading}>
        Create Account
      </Button>
    </form>
  );
}
