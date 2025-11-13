'use client'

import { useState, useEffect } from "react"
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'
import { Calendar as CalendarIcon, CheckSquare, Clock, Star, Users, Search, Filter, X, Eye, Plus } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/lib/auth-context"
import { useTasks } from "@/lib/react-query"

const statusColors = {
  pending: { bg: "#f3f4f6", text: "#374151", border: "#d1d5db" },
  ongoing: { bg: "#dbeafe", text: "#1e40af", border: "#3b82f6" },
  completed: { bg: "#fef3c7", text: "#92400e", border: "#f59e0b" },
  approved: { bg: "#dcfce7", text: "#166534", border: "#22c55e" },
  overdue: { bg: "#fee2e2", text: "#dc2626", border: "#ef4444" }
}

const urgencyColors = {
  low: { bg: "#f9fafb", text: "#374151", border: "#d1d5db" },
  medium: { bg: "#fef3c7", text: "#92400e", border: "#f59e0b" },
  high: { bg: "#fed7aa", text: "#ea580c", border: "#f97316" },
  urgent: { bg: "#fee2e2", text: "#dc2626", border: "#ef4444" }
}

function TaskDetailModal({ task, isOpen, onClose }) {
  if (!task) return null

  const formatDate = (date) => {
    return new Date(date).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const isOverdue = new Date(task.due_date) < new Date() && task.status !== 'approved'

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="text-xl">{task.title}</DialogTitle>
          <DialogDescription className="flex items-center gap-2 mt-2">
            <Badge style={{
              backgroundColor: statusColors[task.status]?.bg,
              color: statusColors[task.status]?.text,
              borderColor: statusColors[task.status]?.border
            }}>
              {task.status}
            </Badge>
            <Badge style={{
              backgroundColor: urgencyColors[task.urgency || 'medium']?.bg,
              color: urgencyColors[task.urgency || 'medium']?.text,
              borderColor: urgencyColors[task.urgency || 'medium']?.border
            }}>
              <div className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full`} style={{
                  backgroundColor: urgencyColors[task.urgency || 'medium']?.text
                }}></div>
                {task.urgency ? task.urgency.charAt(0).toUpperCase() + task.urgency.slice(1) : 'Medium'}
              </div>
            </Badge>
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-[50vh] pr-4">
          <div className="space-y-6">
            {/* Description */}
            <div>
              <h3 className="font-semibold mb-2">Description</h3>
              <p className="text-sm text-muted-foreground">
                {task.description || 'No description provided'}
              </p>
            </div>

            {/* Assignees */}
            <div>
              <h3 className="font-semibold mb-2">Assignees</h3>
              <div className="space-y-2">
                {task.assignments && task.assignments.length > 0 ? (
                  task.assignments.map((assignment) => (
                    <div key={assignment.user_id} className="flex items-center gap-3 p-2 border rounded-lg">
                      <Avatar>
                        <AvatarFallback>
                          {assignment.user_name?.split(' ').map(n => n[0]).join('') || 'U'}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <p className="font-medium">{assignment.user_name}</p>
                        <p className="text-sm text-muted-foreground">{assignment.user_email}</p>
                      </div>
                      {task.team_head_id === assignment.user_id && (
                        <Badge variant="outline">Team Head</Badge>
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">No assignees</p>
                )}
              </div>
            </div>

            <Separator />

            {/* Task Details */}
            <div className="grid gap-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-sm text-muted-foreground">Created By</h4>
                  <p className="text-sm">{task.creator_name || 'Unknown'}</p>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-muted-foreground">Created At</h4>
                  <p className="text-sm">{formatDate(task.created_at)}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-sm text-muted-foreground">Due Date</h4>
                  <p className={`text-sm ${isOverdue ? 'text-red-600 font-medium' : ''}`}>
                    {formatDate(task.due_date)}
                    {isOverdue && <span className="ml-2 text-xs">(Overdue)</span>}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-muted-foreground">Score</h4>
                  <div className="text-sm">
                    {task.score ? (
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 text-yellow-500" />
                        <span>{task.score}/10</span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground">Not scored</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Feedback */}
            {task.feedback && (
              <div>
                <h3 className="font-semibold mb-2">Feedback</h3>
                <div className="p-3 bg-muted rounded-lg">
                  <p className="text-sm">{task.feedback}</p>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function CalendarPage() {
  const { user } = useAuth()
  const [selectedTask, setSelectedTask] = useState(null)
  const [isTaskDetailOpen, setIsTaskDetailOpen] = useState(false)
  const [activeView, setActiveView] = useState('month')
  const [selectedDate, setSelectedDate] = useState(new Date())

  const { data: tasks = [], isLoading } = useTasks()

  // Convert tasks to FullCalendar events
  const calendarEvents = Array.isArray(tasks) ? tasks.map(task => {
    const urgencyColor = urgencyColors[task.urgency || 'medium']
    const statusColor = statusColors[task.status]

    return {
      id: task.id,
      title: task.title,
      start: task.due_date,
      end: task.due_date, // For all-day events, you might want to handle this differently
      backgroundColor: task.status === 'overdue' ? statusColor.bg : urgencyColor.bg,
      borderColor: task.status === 'overdue' ? statusColor.border : urgencyColor.border,
      textColor: task.status === 'overdue' ? statusColor.text : urgencyColor.text,
      extendedProps: {
        task: task,
        status: task.status,
        urgency: task.urgency || 'medium',
        assignees: task.assignments || [],
        description: task.description
      }
    }
  }) : []

  // Handle event click
  const handleEventClick = (clickInfo) => {
    const task = clickInfo.event.extendedProps.task
    setSelectedTask(task)
    setIsTaskDetailOpen(true)
  }

  // Handle date click
  const handleDateClick = (dateClickInfo) => {
    setSelectedDate(new Date(dateClickInfo.dateStr))
  }

  // Get tasks for selected date
  const getTasksForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0]
    return Array.isArray(tasks) ? tasks.filter(task => {
      const taskDate = new Date(task.due_date).toISOString().split('T')[0]
      return taskDate === dateStr
    }) : []
  }

  const selectedDateTasks = getTasksForDate(selectedDate)

  // Calendar statistics
  const tasksArray = Array.isArray(tasks) ? tasks : []
  const myTasks = tasksArray.filter(task =>
    task.assignments?.some(assignment => assignment.user_id === user?.id)
  )
  const upcomingTasks = tasksArray.filter(task => {
    const dueDate = new Date(task.due_date)
    const today = new Date()
    const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
    return dueDate >= today && dueDate <= nextWeek && task.status !== 'approved'
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Calendar</h1>
            <p className="text-muted-foreground">
              View and manage tasks with full calendar interface
            </p>
          </div>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Task
          </Button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tasksArray.length}</div>
            <p className="text-xs text-muted-foreground">
              All tasks in system
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">My Tasks</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{myTasks.length}</div>
            <p className="text-xs text-muted-foreground">
              Assigned to me
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Upcoming</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{upcomingTasks.length}</div>
            <p className="text-xs text-muted-foreground">
              Due this week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasksArray.filter(t => t.status === 'overdue').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Past due date
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Calendar Tabs */}
      <Tabs value={activeView} onValueChange={setActiveView}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="month">Month</TabsTrigger>
          <TabsTrigger value="week">Week</TabsTrigger>
          <TabsTrigger value="day">Day</TabsTrigger>
          <TabsTrigger value="list">List</TabsTrigger>
        </TabsList>

        {/* Main Calendar */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <CardTitle>Task Calendar</CardTitle>
                <CardDescription>
                  Click on tasks to view details. Different colors represent priority levels and status.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex justify-center">
                    <Skeleton className="h-[600px] w-full" />
                  </div>
                ) : (
                  <FullCalendar
                    plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin]}
                    headerToolbar={{
                      left: 'prev,next today',
                      center: 'title',
                      right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
                    }}
                    initialView={
                      activeView === 'month' ? 'dayGridMonth' :
                      activeView === 'week' ? 'timeGridWeek' :
                      activeView === 'day' ? 'timeGridDay' : 'listMonth'
                    }
                    events={calendarEvents}
                    eventClick={handleEventClick}
                    dateClick={handleDateClick}
                    height="auto"
                    dayMaxEvents={3}
                    moreLinkClick="popover"
                    eventDisplay="block"
                    displayEventTime={false}
                    eventMouseEnter={(info) => {
                      info.el.title = `${info.event.title}\nStatus: ${info.event.extendedProps.status}\nPriority: ${info.event.extendedProps.urgency}`
                    }}
                    eventClassNames="cursor-pointer hover:opacity-80 transition-opacity"
                    dayHeaderClassNames="text-sm font-medium"
                    viewDidMount={() => {
                      // Custom styling after calendar renders
                      const style = document.createElement('style')
                      style.innerHTML = `
                        .fc-event {
                          font-size: 0.75rem;
                          padding: 2px 4px;
                          border-radius: 4px;
                          border-width: 1px;
                        }
                        .fc-daygrid-event {
                          margin-bottom: 2px;
                        }
                        .fc-event-title {
                          font-weight: 500;
                        }
                      `
                      document.head.appendChild(style)
                    }}
                  />
                )}

                {/* Legend */}
                <div className="flex flex-wrap items-center gap-4 mt-4 text-sm border-t pt-4">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded border" style={{ backgroundColor: urgencyColors.low.bg, borderColor: urgencyColors.low.border }}></div>
                    <span>Low Priority</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded border" style={{ backgroundColor: urgencyColors.medium.bg, borderColor: urgencyColors.medium.border }}></div>
                    <span>Medium Priority</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded border" style={{ backgroundColor: urgencyColors.high.bg, borderColor: urgencyColors.high.border }}></div>
                    <span>High Priority</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded border" style={{ backgroundColor: urgencyColors.urgent.bg, borderColor: urgencyColors.urgent.border }}></div>
                    <span>Urgent Priority</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded border" style={{ backgroundColor: statusColors.overdue.bg, borderColor: statusColors.overdue.border }}></div>
                    <span>Overdue Tasks</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Tasks for selected date */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">
                  {selectedDate.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                </CardTitle>
                <CardDescription>
                  {selectedDateTasks.length} task{selectedDateTasks.length !== 1 ? 's' : ''} due
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[500px]">
                  {selectedDateTasks.length > 0 ? (
                    <div className="space-y-3">
                      {selectedDateTasks.map((task) => (
                        <div
                          key={task.id}
                          className="p-3 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                          onClick={() => {
                            setSelectedTask(task)
                            setIsTaskDetailOpen(true)
                          }}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-medium text-sm line-clamp-2">{task.title}</h4>
                            <Badge
                              variant="outline"
                              style={{
                                backgroundColor: urgencyColors[task.urgency || 'medium']?.bg,
                                color: urgencyColors[task.urgency || 'medium']?.text,
                                borderColor: urgencyColors[task.urgency || 'medium']?.border
                              }}
                            >
                              {(task.urgency || 'medium').charAt(0).toUpperCase() + (task.urgency || 'medium').slice(1)}
                            </Badge>
                          </div>

                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1">
                              {task.type === 'individual' ? (
                                <div className="flex items-center gap-1">
                                  <Avatar className="h-4 w-4">
                                    <AvatarFallback className="text-xs">
                                      {task.assignments?.[0]?.user_name?.split(' ').map(n => n[0]).join('') || 'U'}
                                    </AvatarFallback>
                                  </Avatar>
                                  <span className="text-xs text-muted-foreground">{task.assignments?.[0]?.user_name}</span>
                                </div>
                              ) : (
                                <div className="flex items-center gap-1">
                                  <Users className="h-3 w-3" />
                                  <span className="text-xs text-muted-foreground">{task.assignments?.length || 0} members</span>
                                </div>
                              )}
                            </div>

                            <Badge
                              style={{
                                backgroundColor: statusColors[task.status]?.bg,
                                color: statusColors[task.status]?.text,
                                borderColor: statusColors[task.status]?.border
                              }}
                            >
                              {task.status}
                            </Badge>
                          </div>

                          {task.score && (
                            <div className="flex items-center gap-1 mt-2">
                              <Star className="h-3 w-3 text-yellow-500" />
                              <span className="text-xs">{task.score}/10</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <CalendarIcon className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                      <h3 className="font-medium mb-1">No tasks due</h3>
                      <p className="text-muted-foreground text-sm">
                        No tasks are scheduled for this date.
                      </p>
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </div>
      </Tabs>

      {/* Task Detail Modal */}
      <TaskDetailModal
        task={selectedTask}
        isOpen={isTaskDetailOpen}
        onClose={() => {
          setIsTaskDetailOpen(false)
          setSelectedTask(null)
        }}
      />
    </div>
  )
}