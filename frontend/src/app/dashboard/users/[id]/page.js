"use client"

import React, { useMemo } from "react"
import { useParams, useRouter } from "next/navigation"
import {
  ArrowLeft,
  User,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  Building2,
  Calendar,
  Target,
  ListChecks,
  Award,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
} from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { useUsers, useGoals, useSuperviseeGoals } from "@/lib/react-query"

const statusColors = {
  PENDING_APPROVAL: "bg-yellow-100 text-yellow-800 border-yellow-200",
  ACTIVE: "bg-blue-100 text-blue-800 border-blue-200",
  ACHIEVED: "bg-green-100 text-green-800 border-green-200",
  DISCARDED: "bg-gray-100 text-gray-800 border-gray-200",
  REJECTED: "bg-red-100 text-red-800 border-red-200",
}

const initiativeStatusColors = {
  PENDING_APPROVAL: "bg-yellow-100 text-yellow-800",
  ASSIGNED: "bg-blue-100 text-blue-800",
  PENDING: "bg-gray-100 text-gray-800",
  ONGOING: "bg-blue-100 text-blue-800",
  UNDER_REVIEW: "bg-purple-100 text-purple-800",
  COMPLETED: "bg-green-100 text-green-800",
  REJECTED: "bg-red-100 text-red-800",
  OVERDUE: "bg-red-100 text-red-800",
}

function GoalCard({ goal }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <CardTitle className="text-base font-semibold">{goal.title}</CardTitle>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={statusColors[goal.status]}>
                {goal.status?.replace(/_/g, ' ')}
              </Badge>
              {goal.quarter && goal.year && (
                <Badge variant="outline">{goal.quarter} {goal.year}</Badge>
              )}
              {goal.tags && goal.tags.length > 0 && goal.tags.map((tag) => (
                <Badge
                  key={tag.id}
                  variant="outline"
                  className="text-xs"
                  style={{ borderColor: tag.color, color: tag.color }}
                >
                  {tag.name}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {goal.description && (
          <div
            className="text-sm text-gray-600 line-clamp-2 prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: goal.description }}
          />
        )}

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Progress</span>
            <span className="font-semibold">{goal.progress_percentage || 0}%</span>
          </div>
          <Progress value={goal.progress_percentage || 0} className="h-2" />
        </div>

        {(goal.start_date || goal.end_date) && (
          <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t">
            {goal.start_date && (
              <div className="flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" />
                {new Date(goal.start_date).toLocaleDateString()}
              </div>
            )}
            {goal.end_date && (
              <div>Due: {new Date(goal.end_date).toLocaleDateString()}</div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function InitiativeCard({ initiative }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <CardTitle className="text-base font-semibold">{initiative.title}</CardTitle>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={initiativeStatusColors[initiative.status]}>
                {initiative.status?.replace(/_/g, ' ')}
              </Badge>
              {initiative.urgency && (
                <Badge variant="outline">{initiative.urgency}</Badge>
              )}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {initiative.description && (
          <p className="text-sm text-gray-600 line-clamp-2">{initiative.description}</p>
        )}

        {initiative.score && (
          <div className="flex items-center gap-2">
            <Award className="h-4 w-4 text-yellow-600" />
            <span className="text-sm font-medium">Score: {initiative.score}/10</span>
          </div>
        )}

        {initiative.due_date && (
          <div className="flex items-center gap-1 text-xs text-gray-500 pt-2 border-t">
            <Clock className="h-3.5 w-3.5" />
            Due: {new Date(initiative.due_date).toLocaleDateString()}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function UserDetailPage() {
  const params = useParams()
  const router = useRouter()
  const userId = params.id

  const { data: users = [], isLoading: isLoadingUsers } = useUsers()
  const { data: allGoals = [], isLoading: isLoadingGoals } = useGoals()

  // Find the user
  const user = useMemo(() => {
    return users.find(u => u.id === userId)
  }, [users, userId])

  // Get user's goals
  const userGoals = useMemo(() => {
    return allGoals.filter(g => g.owner_id === userId)
  }, [allGoals, userId])

  // Get user's supervisor
  const supervisor = useMemo(() => {
    if (!user?.supervisor_id) return null
    return users.find(u => u.id === user.supervisor_id)
  }, [user, users])

  // Get user's organization
  const organization = user?.organization_name || "Unknown"

  // Calculate statistics
  const stats = useMemo(() => {
    const totalGoals = userGoals.length
    const activeGoals = userGoals.filter(g => g.status === 'ACTIVE').length
    const achievedGoals = userGoals.filter(g => g.status === 'ACHIEVED').length
    const avgProgress = totalGoals > 0
      ? Math.round(userGoals.reduce((sum, g) => sum + (g.progress_percentage || 0), 0) / totalGoals)
      : 0

    return {
      totalGoals,
      activeGoals,
      achievedGoals,
      avgProgress,
    }
  }, [userGoals])

  if (isLoadingUsers || isLoadingGoals) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-12 w-64" />
        <div className="grid gap-6 md:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <User className="h-16 w-16 text-gray-400 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">User Not Found</h2>
        <p className="text-gray-600 mb-4">The user you're looking for doesn't exist.</p>
        <Button onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Go Back
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b border-gray-200 pb-6">
        <Button
          variant="ghost"
          onClick={() => router.back()}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>

        <div className="flex items-start gap-6">
          <Avatar className="h-24 w-24">
            <AvatarFallback className="text-2xl bg-blue-100 text-blue-700">
              {user.name.split(' ').map(n => n[0]).join('').toUpperCase()}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1 space-y-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{user.name}</h1>
              <p className="text-lg text-gray-600">{user.job_title || 'No title'}</p>
            </div>

            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {user.email && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Mail className="h-4 w-4" />
                  <span>{user.email}</span>
                </div>
              )}
              {user.phone && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Phone className="h-4 w-4" />
                  <span>{user.phone}</span>
                </div>
              )}
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Building2 className="h-4 w-4" />
                <span>{organization}</span>
              </div>
              {supervisor && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <User className="h-4 w-4" />
                  <span>Reports to: {supervisor.name}</span>
                </div>
              )}
              {user.level && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Briefcase className="h-4 w-4" />
                  <span>Level: {user.level}</span>
                </div>
              )}
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Badge className={`${user.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                  {user.status}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Goals</CardTitle>
            <Target className="h-4 w-4 text-gray-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalGoals}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Active Goals</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.activeGoals}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Achieved Goals</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.achievedGoals}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Avg Progress</CardTitle>
            <Award className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.avgProgress}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Info */}
      {(user.skillset || user.address) && (
        <Card>
          <CardHeader>
            <CardTitle>Additional Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {user.skillset && (
              <div>
                <h3 className="font-semibold text-sm text-gray-700 mb-2">Skillset</h3>
                <p className="text-sm text-gray-600">{user.skillset}</p>
              </div>
            )}
            {user.address && (
              <div>
                <h3 className="font-semibold text-sm text-gray-700 mb-2 flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Address
                </h3>
                <p className="text-sm text-gray-600">{user.address}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tabs for Goals and Initiatives */}
      <Tabs defaultValue="goals" className="space-y-6">
        <TabsList>
          <TabsTrigger value="goals" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Goals ({userGoals.length})
          </TabsTrigger>
          <TabsTrigger value="initiatives" className="flex items-center gap-2">
            <ListChecks className="h-4 w-4" />
            Initiatives
          </TabsTrigger>
        </TabsList>

        <TabsContent value="goals" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Goals</CardTitle>
              <CardDescription>
                All goals assigned to or created by this user
              </CardDescription>
            </CardHeader>
            <CardContent>
              {userGoals.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {userGoals.map((goal) => (
                    <GoalCard key={goal.id} goal={goal} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No goals yet</h3>
                  <p className="text-gray-600">This user hasn't created any goals yet.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="initiatives" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Initiatives</CardTitle>
              <CardDescription>
                All initiatives assigned to this user
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <ListChecks className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Coming soon</h3>
                <p className="text-gray-600">Initiative tracking will be available here.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
