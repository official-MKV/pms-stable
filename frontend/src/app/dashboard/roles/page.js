'use client'

import { useState } from "react"
import { Plus, Shield, Users, MoreHorizontal, Edit, Trash2, Eye, Copy, Settings } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { PermissionGuard } from "@/lib/auth-context"
import {
  useRoles,
  usePermissions,
  useCreateRole,
  useUpdateRole,
  useDeleteRole,
} from "@/lib/react-query"
import RoleForm from "@/components/dashboard/RoleForm"

const scopeOverrideOptions = {
  none: {
    label: "None (Organizational Scope)",
    description: "Access limited to user's organizational level and below",
    color: "bg-gray-100 text-gray-800"
  },
  global: {
    label: "Global Access",
    description: "Access to all organizational data across the entire system",
    color: "bg-blue-100 text-blue-800"
  },
  cross_directorate: {
    label: "Cross-Directorate",
    description: "Access data across multiple directorates",
    color: "bg-purple-100 text-purple-800"
  }
}
 
const formatPermissionName = (permission) => {
  return permission.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function RoleDetailsDialog({ role, isOpen, onClose }) {
  if (!role) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            {role.name}
          </DialogTitle>
          <DialogDescription>
            Role details and permissions
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div>
            <Label className="text-sm font-medium text-muted-foreground">Description</Label>
            <p className="mt-1">{role.description || 'No description provided'}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium text-muted-foreground">Access Scope</Label>
              <Badge className={`mt-1 ${scopeOverrideOptions[role.scope_override || 'none'].color}`}>
                {scopeOverrideOptions[role.scope_override || 'none'].label}
              </Badge>
            </div>
            <div>
              <Label className="text-sm font-medium text-muted-foreground">Leadership Role</Label>
              <p className="mt-1">{role.is_leadership ? 'Yes' : 'No'}</p>
            </div>
          </div>

          <div>
            <Label className="text-sm font-medium text-muted-foreground">
              Permissions ({role.permissions?.length || 0})
            </Label>
            <div className="mt-2 flex flex-wrap gap-1 max-h-48 overflow-y-auto">
              {role.permissions && role.permissions.length > 0 ? (
                role.permissions.map((permission) => (
                  <Badge key={permission} variant="outline" className="text-xs">
                    {formatPermissionName(permission)}
                  </Badge>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No permissions assigned</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium text-muted-foreground">Created</Label>
              <p className="mt-1 text-sm">{new Date(role.created_at).toLocaleDateString()}</p>
            </div>
            <div>
              <Label className="text-sm font-medium text-muted-foreground">Users</Label>
              <p className="mt-1 text-sm">{role.user_count || 0} assigned</p>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function RolesPage() {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isDetailsOpen, setIsDetailsOpen] = useState(false)
  const [editingRole, setEditingRole] = useState(null)
  const [viewingRole, setViewingRole] = useState(null)
  const [searchQuery, setSearchQuery] = useState("")

  const { data: roles = [], isLoading } = useRoles()
  const { data: permissions = {} } = usePermissions()
  const createMutation = useCreateRole()
  const updateMutation = useUpdateRole()
  const deleteMutation = useDeleteRole()

  const handleCreate = (data) => {
    createMutation.mutate(data)
  }

  const handleUpdate = (data) => {
    if (editingRole) {
      updateMutation.mutate({ id: editingRole.id, ...data })
    }
  }

  const handleEdit = (role) => {
    setEditingRole(role)
    setIsFormOpen(true)
  }

  const handleView = (role) => {
    setViewingRole(role)
    setIsDetailsOpen(true)
  }

  const handleDuplicate = (role) => {
    setEditingRole({
      ...role,
      id: null,
      name: `${role.name} (Copy)`,
      user_count: 0
    })
    setIsFormOpen(true)
  }

  const handleDelete = (role) => {
    if (role.user_count > 0) {
      alert(`Cannot delete role "${role.name}" because it is assigned to ${role.user_count} users.`)
      return
    }

    if (confirm(`Are you sure you want to delete the role "${role.name}"?`)) {
      deleteMutation.mutate(role.id)
    }
  }

  const handleCloseForm = () => {
    setIsFormOpen(false)
    setEditingRole(null)
  }

  const rolesArray = Array.isArray(roles) ? roles : []
  const filteredRoles = rolesArray.filter(role =>
    role.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    role.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Group roles by scope for better organization
  const rolesByScope = filteredRoles.reduce((acc, role) => {
    const scope = role.scope_override || 'none'
    if (!acc[scope]) acc[scope] = []
    acc[scope].push(role)
    return acc
  }, {})

  return (
    <PermissionGuard permission="role_create">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Role Management</h1>
              <p className="text-muted-foreground">
                Create and manage roles with specific permissions and access scope
              </p>
            </div>
            <Button onClick={() => setIsFormOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Role
            </Button>
          </div>
        </div>

        {/* Search and Statistics */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="md:col-span-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Search Roles</CardTitle>
            </CardHeader>
            <CardContent>
              <Input
                placeholder="Search roles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Roles</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{filteredRoles.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Leadership Roles</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {filteredRoles.filter(role => role.is_leadership).length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Global Access</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {filteredRoles.filter(role => role.scope_override === 'global').length}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Roles Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Roles ({filteredRoles.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : filteredRoles.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Role</TableHead>
                    <TableHead>Access Scope</TableHead>
                    <TableHead>Permissions</TableHead>
                    <TableHead>Users</TableHead>
                    <TableHead>Leadership</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredRoles.map((role) => (
                    <TableRow key={role.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{role.name}</div>
                          <div className="text-sm text-muted-foreground line-clamp-1">
                            {role.description || 'No description'}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={scopeOverrideOptions[role.scope_override || 'none'].color}>
                          {scopeOverrideOptions[role.scope_override || 'none'].label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">
                            {role.permissions?.length || 0} permissions
                          </Badge>
                          {role.permissions?.includes('system_admin') && (
                            <Badge variant="destructive" className="text-xs">
                              Super Admin
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Users className="h-4 w-4 text-muted-foreground" />
                          <span>{role.user_count || 0}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {role.is_leadership ? (
                          <Badge variant="outline" className="bg-blue-50 text-blue-700">
                            Yes
                          </Badge>
                        ) : (
                          <span className="text-muted-foreground">No</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleView(role)}>
                              <Eye className="mr-2 h-4 w-4" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleEdit(role)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleDuplicate(role)}>
                              <Copy className="mr-2 h-4 w-4" />
                              Duplicate
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => handleDelete(role)}
                              className="text-red-600"
                              disabled={role.user_count > 0}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-12">
                <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No roles found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchQuery
                    ? 'No roles match your search criteria.'
                    : 'Get started by creating your first role.'}
                </p>
                <Button onClick={() => setIsFormOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Role
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Dialogs */}
        <RoleForm
          role={editingRole}
          isOpen={isFormOpen}
          onClose={handleCloseForm}
          onSubmit={editingRole ? handleUpdate : handleCreate}
        />

        <RoleDetailsDialog
          role={viewingRole}
          isOpen={isDetailsOpen}
          onClose={() => {
            setIsDetailsOpen(false)
            setViewingRole(null)
          }}
        />
      </div>
    </PermissionGuard>
  )
}