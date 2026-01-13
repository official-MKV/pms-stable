'use client'

import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useWebSocket } from './useWebSocket'
import { useAuth } from './auth-context'
import { useQueryClient } from '@tanstack/react-query'

const NotificationContext = createContext(undefined)

export function NotificationProvider({ children }) {
  const { user } = useAuth()
  const { isConnected, lastMessage } = useWebSocket()
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const queryClient = useQueryClient()

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!lastMessage) return

    if (lastMessage.type === 'new_notification') {
      const newNotification = lastMessage.notification

      // Add to local state
      setNotifications(prev => [newNotification, ...prev])
      setUnreadCount(prev => prev + 1)

      // Show toast notification (optional - you can add toast library later)
      console.log('New notification:', newNotification.title)

      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    } else if (lastMessage.type === 'marked_read') {
      // Update local state when marked as read
      const notificationId = lastMessage.notification_id
      setNotifications(prev =>
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    }
  }, [lastMessage, queryClient])

  const addNotification = useCallback((notification) => {
    setNotifications(prev => [notification, ...prev])
    if (!notification.is_read) {
      setUnreadCount(prev => prev + 1)
    }
  }, [])

  const markAsRead = useCallback((notificationId) => {
    setNotifications(prev =>
      prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
    )
    setUnreadCount(prev => Math.max(0, prev - 1))
  }, [])

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
    setUnreadCount(0)
  }, [])

  const removeNotification = useCallback((notificationId) => {
    setNotifications(prev => {
      const notification = prev.find(n => n.id === notificationId)
      if (notification && !notification.is_read) {
        setUnreadCount(count => Math.max(0, count - 1))
      }
      return prev.filter(n => n.id !== notificationId)
    })
  }, [])

  const setInitialNotifications = useCallback((initialNotifications, initialUnreadCount) => {
    setNotifications(initialNotifications)
    setUnreadCount(initialUnreadCount)
  }, [])

  const value = {
    notifications,
    unreadCount,
    isConnected,
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    setInitialNotifications
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  )
}

export function useNotifications() {
  const context = useContext(NotificationContext)
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}
