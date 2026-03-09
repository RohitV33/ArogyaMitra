// authStore.ts - Zustand State Management for ArogyaMitra
// Matches the interface shown in Activity 4.4 screenshots

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// ─── User Interface (exact fields from screenshot) ────────────────────────────
interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'user' | 'admin';
  is_active: boolean;
  fitness_level?: string;
  fitness_goal?: string;
  workout_preference?: string;
  diet_preference?: string;
  streak_points: number;
  total_workouts: number;
  charity_donations: number;
  phone?: string;
  age?: number;
  height?: number;
  weight?: number;
  gender?: string;
  bio?: string;
  profile_photo_url?: string;
}

// ─── Auth Store State ─────────────────────────────────────────────────────────
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  login: (token: string, user: User) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  incrementStreak: () => void;
  incrementWorkouts: () => void;
  addCharityDonation: (amount: number) => void;
  setLoading: (loading: boolean) => void;
}

// ─── Workout Store ────────────────────────────────────────────────────────────
interface WorkoutState {
  currentPlan: any | null;
  planHistory: any[];
  completedExercises: Record<string, boolean>;
  setCurrentPlan: (plan: any) => void;
  addToHistory: (plan: any) => void;
  markExerciseComplete: (exerciseId: string) => void;
  resetCompletedExercises: () => void;
}

// ─── Nutrition Store ──────────────────────────────────────────────────────────
interface NutritionState {
  currentPlan: any | null;
  completedMeals: Record<string, boolean>;
  setNutritionPlan: (plan: any) => void;
  markMealComplete: (mealId: string) => void;
  resetMeals: () => void;
}

// ─── Chat Store ───────────────────────────────────────────────────────────────
interface ChatMessage {
  id: string;
  type: 'user' | 'aromi';
  content: string;
  timestamp: Date;
}

interface ChatState {
  messages: ChatMessage[];
  isOpen: boolean;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  setOpen: (open: boolean) => void;
}

// ─── Progress Store ───────────────────────────────────────────────────────────
interface ProgressState {
  records: any[];
  analytics: any | null;
  addRecord: (record: any) => void;
  setAnalytics: (analytics: any) => void;
}

// ─── Body Metrics ─────────────────────────────────────────────────────────────
interface BodyMetrics {
  bmi?: number;
  bodyFatPercent?: number;
  muscleMass?: number;
  waistCircumference?: number;
  age?: number;
  gender?: string;
  height?: number;
  weight?: number;
  timestamp?: string;
}

interface BodyMetricsState {
  metrics: BodyMetrics | null;
  setMetrics: (metrics: BodyMetrics) => void;
  clearMetrics: () => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// AUTH STORE (with persist middleware for localStorage)
// ═══════════════════════════════════════════════════════════════════════════════
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => set({ user, isAuthenticated: true }),
      setToken: (token) => set({ token }),

      login: (token, user) => {
        localStorage.setItem('arogyamitra_token', token);
        set({ token, user, isAuthenticated: true, isLoading: false });
      },

      logout: () => {
        localStorage.removeItem('arogyamitra_token');
        set({ token: null, user: null, isAuthenticated: false });
      },

      updateUser: (updates) => {
        const current = get().user;
        if (current) {
          set({ user: { ...current, ...updates } });
        }
      },

      incrementStreak: () => {
        const user = get().user;
        if (user) {
          set({ user: { ...user, streak_points: user.streak_points + 1 } });
        }
      },

      incrementWorkouts: () => {
        const user = get().user;
        if (user) {
          set({ user: { ...user, total_workouts: user.total_workouts + 1 } });
        }
      },

      addCharityDonation: (amount) => {
        const user = get().user;
        if (user) {
          set({ user: { ...user, charity_donations: user.charity_donations + amount } });
        }
      },

      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'arogyamitra-auth',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// ═══════════════════════════════════════════════════════════════════════════════
// WORKOUT STORE
// ═══════════════════════════════════════════════════════════════════════════════
export const useWorkoutStore = create<WorkoutState>()(
  persist(
    (set, get) => ({
      currentPlan: null,
      planHistory: [],
      completedExercises: {},

      setCurrentPlan: (plan) => set({ currentPlan: plan }),

      addToHistory: (plan) => {
        const history = get().planHistory;
        set({ planHistory: [plan, ...history].slice(0, 10) }); // Keep last 10
      },

      markExerciseComplete: (exerciseId) => {
        set((state) => ({
          completedExercises: {
            ...state.completedExercises,
            [exerciseId]: true,
          },
        }));
      },

      resetCompletedExercises: () => set({ completedExercises: {} }),
    }),
    { name: 'arogyamitra-workouts' }
  )
);

// ═══════════════════════════════════════════════════════════════════════════════
// NUTRITION STORE
// ═══════════════════════════════════════════════════════════════════════════════
export const useNutritionStore = create<NutritionState>()(
  persist(
    (set) => ({
      currentPlan: null,
      completedMeals: {},

      setNutritionPlan: (plan) => set({ currentPlan: plan }),

      markMealComplete: (mealId) => {
        set((state) => ({
          completedMeals: {
            ...state.completedMeals,
            [mealId]: !state.completedMeals[mealId],
          },
        }));
      },

      resetMeals: () => set({ completedMeals: {} }),
    }),
    { name: 'arogyamitra-nutrition' }
  )
);

// ═══════════════════════════════════════════════════════════════════════════════
// CHAT STORE (AROMI history)
// ═══════════════════════════════════════════════════════════════════════════════
export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [
        {
          id: '1',
          type: 'aromi',
          content: '🙏 Namaste! I\'m AROMI, your personal health companion powered by ArogyaMitra! 💚 How can I help you on your wellness journey today?',
          timestamp: new Date(),
        },
      ],
      isOpen: false,

      addMessage: (message) => {
        set((state) => ({
          messages: [...state.messages, message].slice(-100), // Keep last 100 messages
        }));
      },

      clearMessages: () =>
        set({
          messages: [
            {
              id: Date.now().toString(),
              type: 'aromi',
              content: '🙏 Namaste! I\'m AROMI, your personal health companion. How can I help you today?',
              timestamp: new Date(),
            },
          ],
        }),

      setOpen: (isOpen) => set({ isOpen }),
    }),
    {
      name: 'arogyamitra-chat',
      partialize: (state) => ({ messages: state.messages.slice(-20) }), // Persist only last 20
    }
  )
);

// ═══════════════════════════════════════════════════════════════════════════════
// PROGRESS STORE
// ═══════════════════════════════════════════════════════════════════════════════
export const useProgressStore = create<ProgressState>()(
  persist(
    (set, get) => ({
      records: [],
      analytics: null,

      addRecord: (record) => {
        set((state) => ({
          records: [record, ...state.records].slice(0, 90), // Keep 90 days
        }));
      },

      setAnalytics: (analytics) => set({ analytics }),
    }),
    { name: 'arogyamitra-progress' }
  )
);

// ═══════════════════════════════════════════════════════════════════════════════
// BODY METRICS STORE
// ═══════════════════════════════════════════════════════════════════════════════
export const useBodyMetricsStore = create<BodyMetricsState>()(
  persist(
    (set) => ({
      metrics: null,
      setMetrics: (metrics) => set({ metrics: { ...metrics, timestamp: new Date().toISOString() } }),
      clearMetrics: () => set({ metrics: null }),
    }),
    { name: 'arogyamitra-body-metrics' }
  )
);
