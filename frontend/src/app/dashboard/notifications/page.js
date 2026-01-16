'use client'

import { useState } from "react"
import { Bell, Check, CheckCheck, Trash2, ExternalLink, Filter, Search, X } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useNotifications as useNotificationsContext } from "@/lib/notification-context"
import { useNotifications, useMarkNotificationAsRead, useMarkAllNotificationsAsRead, useDeleteNotification } from "@/lib/react-query"
import { toast } from "sonner"
import { useRouter } from "next/navigation"
import { format } from "date-fns"

const notificationTypeColors = {
  INITIATIVE_ASSIGNED: "bg-blue-100 text-blue-800 border-blue-200",
  INITIATIVE_APPROVED: "bg-green-100 text-green-800 border-green-200",
  INITIATIVE_REJECTED: "bg-red-100 text-red-800 border-red-200",
  INITIATIVE_STATUS_CHANGED: "bg-purple-100 text-purple-800 border-purple-200",
  INITIATIVE_SUBMITTED: "bg-indigo-100 text-indigo-800 border-indigo-200",
  INITIATIVE_REVIEWED: "bg-teal-100 text-teal-800 border-teal-200",
  INITIATIVE_DEADLINE_APPROACHING: "bg-orange-100 text-orange-800 border-orange-200",
  GOAL_ASSIGNED: "bg-blue-100 text-blue-800 border-blue-200",
  GOAL_APPROVED: "bg-green-100 text-green-800 border-green-200",
  GOAL_REJECTED: "bg-red-100 text-red-800 border-red-200",
  GOAL_PROGRESS_UPDATED: "bg-cyan-100 text-cyan-800 border-cyan-200",
  GOAL_STATUS_CHANGED: "bg-purple-100 text-purple-800 border-purple-200",
  GOAL_DEADLINE_APPROACHING: "bg-orange-100 text-orange-800 border-orange-200",
  TASK_ASSIGNED: "bg-blue-100 text-blue-800 border-blue-200",
  TASK_SUBMITTED: "bg-indigo-100 text-indigo-800 border-indigo-200",
  TASK_REVIEWED: "bg-teal-100 text-teal-800 border-teal-200",
  TASK_STATUS_CHANGED: "bg-purple-100 text-purple-800 border-purple-200",
  TASK_DEADLINE_APPROACHING: "bg-orange-100 text-orange-800 border-orange-200",
  USER_ROLE_CHANGED: "bg-violet-100 text-violet-800 border-violet-200",
  USER_STATUS_CHANGED: "bg-gray-100 text-gray-800 border-gray-200",
  GENERAL: "bg-gray-100 text-gray-800 border-gray-200",
}

const priorityColors = {
  LOW: "bg-gray-100 text-gray-800",
  NORMAL: "bg-blue-100 text-blue-800",
  HIGH: "bg-orange-100 text-orange-800",
  URGENT: "bg-red-100 text-red-800",
}

export default function NotificationsPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState("")
  const [typeFilter, setTypeFilter] = useState("all")
  const [priorityFilter, setPriorityFilter] = useState("all")
  const [unreadOnly, setUnreadOnly] = useState(false)

  const { data: notificationsData, isLoading, refetch } = useNotifications({
    unread_only: unreadOnly,
    notification_type: typeFilter !== "all" ? typeFilter : undefined,
    priority: priorityFilter !== "all" ? priorityFilter : undefined,
  })

  const markAsReadMutation = useMarkNotificationAsRead()
  const markAllAsReadMutation = useMarkAllNotificationsAsRead()
  const deleteNotificationMutation = useDeleteNotification()

  const notifications = notificationsData?.notifications || []
  const unreadCount = notificationsData?.unread_count || 0

  const handleMarkAsRead = async (notificationId) => {
    try {
      await markAsReadMutation.mutateAsync(notificationId)
      toast.success("Notification marked as read")
      refetch()
    } catch (error) {
      toast.error("Failed to mark notification as read")
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await markAllAsReadMutation.mutateAsync()
      toast.success("All notifications marked as read")
      refetch()
    } catch (error) {
      toast.error("Failed to mark all notifications as read")
    }
  }

  const handleDeleteNotification = async (notificationId) => {
    try {
      await deleteNotificationMutation.mutateAsync(notificationId)
      toast.success("Notification deleted")
      refetch()
    } catch (error) {
      toast.error("Failed to delete notification")
    }
  }

  const handleNotificationClick = (notification) => {
    // Mark as read if unread
    if (!notification.is_read) {
      handleMarkAsRead(notification.id)
    }

    // Navigate to action URL if available
    if (notification.action_url) {
      router.push(notification.action_url)
    }
  }

  // Filter notifications by search query
  const filteredNotifications = notifications.filter(notification => {
    const matchesSearch = !searchQuery ||
      notification.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      notification.message.toLowerCase().includes(searchQuery.toLowerCase())

    return matchesSearch
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Notifications</h1>
          <p className="text-muted-foreground">
            Stay updated with your activities and assignments
          </p>
        </div>
        {unreadCount > 0 && (
          <Button onClick={handleMarkAllAsRead} variant="outline">
            <CheckCheck className="mr-2 h-4 w-4" />
            Mark All as Read ({unreadCount})
          </Button>
        )}
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search notifications..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="INITIATIVE_ASSIGNED">Initiative Assigned</SelectItem>
                  <SelectItem value="INITIATIVE_APPROVED">Initiative Approved</SelectItem>
                  <SelectItem value="GOAL_ASSIGNED">Goal Assigned</SelectItem>
                  <SelectItem value="TASK_ASSIGNED">Task Assigned</SelectItem>
                </SelectContent>
              </Select>
              <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Priorities</SelectItem>
                  <SelectItem value="LOW">Low</SelectItem>
                  <SelectItem value="NORMAL">Normal</SelectItem>
                  <SelectItem value="HIGH">High</SelectItem>
                  <SelectItem value="URGENT">Urgent</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant={unreadOnly ? "default" : "outline"}
                size="sm"
                onClick={() => setUnreadOnly(!unreadOnly)}
              >
                {unreadOnly ? "Showing Unread" : "Show Unread Only"}
              </Button>
              {(searchQuery || typeFilter !== "all" || priorityFilter !== "all") && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSearchQuery("")
                    setTypeFilter("all")
                    setPriorityFilter("all")
                  }}
                >
                  <X className="mr-2 h-4 w-4" />
                  Clear Filters
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-start gap-4 p-4 border rounded-lg">
                  <Skeleton className="h-12 w-12 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-full" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div className="text-center py-12">
              <Bell className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No notifications</h3>
              <p className="text-sm text-muted-foreground">
                {unreadOnly ? "You have no unread notifications" : "You're all caught up!"}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`flex items-start gap-4 p-4 border rounded-lg transition-colors cursor-pointer hover:bg-muted/50 ${
                    !notification.is_read ? "bg-blue-50 border-blue-200" : ""
                  }`}
                  onClick={() => handleNotificationClick(notification)}
                >
                  <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
                    !notification.is_read ? "bg-blue-500" : "bg-gray-300"
                  }`}>
                    <Bell className="h-5 w-5 text-white" />
                  </div>

                  <div className="flex-1 space-y-1">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className={`font-semibold ${!notification.is_read ? "text-blue-900" : ""}`}>
                            {notification.title}
                          </p>
                          <Badge variant="outline" className={notificationTypeColors[notification.type] || notificationTypeColors.GENERAL}>
                            {notification.type.replace(/_/g, " ")}
                          </Badge>
                          <Badge variant="outline" className={priorityColors[notification.priority]}>
                            {notification.priority}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {notification.message}
                        </p>
                        {notification.triggered_by_name && (
                          <p className="text-xs text-muted-foreground mt-1">
                            By {notification.triggered_by_name}
                          </p>
                        )}
                      </div>

                      <div className="flex items-center gap-1">
                        {!notification.is_read && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleMarkAsRead(notification.id)
                            }}
                          >
                            <Check className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteNotification(notification.id)
                          }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{format(new Date(notification.created_at), "PPp")}</span>
                      {notification.action_url && (
                        <span className="flex items-center gap-1 text-blue-600">
                          <ExternalLink className="h-3 w-3" />
                          View Details
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
