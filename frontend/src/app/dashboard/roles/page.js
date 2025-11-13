'use client'

import { useState } from "react"
import { Plus, Shield, Users, MoreHorizontal, Edit, Trash2, Eye, Copy, Settings } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
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
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { PermissionGuard } from "@/lib/auth-context"
import {
  useRoles,
  usePermissions,
  useCreateRole,
  useUpdateRole,
  useDeleteRole,
} from "@/lib/react-query"

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

// Permission categories for organized display
const permissionCategories = {
  'Organization Management': [
    'organization_create',
    'organization_edit',
    'organization_delete',
    'organization_view_all'
  ],
  'User Management': [
    'user_create',
    'user_edit',
    'user_suspend',
    'user_activate',
    'user_archive',
    'user_view_all',
    'user_history_view'
  ],
  'Role Management': [
    'role_create',
    'role_edit',
    'role_delete',
    'role_assign',
    'role_view_all'
  ],
  'Goal Management': [
    'goal_create_yearly',
    'goal_create_quarterly',
    'goal_create_departmental',
    'goal_edit',
    'goal_progress_update',
    'goal_status_change',
    'goal_view_all'
  ],
  'Task Management': [
    'task_create',
    'task_assign',
    'task_edit',
    'task_review',
    'task_view_all',
    'task_extend_deadline',
    'task_delete'
  ],
  'System Administration': [
    'system_admin',
    'reports_generate',
    'audit_access',
    'notification_manage',
    'backup_access'
  ]
}

function RoleForm({ role, isOpen, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: role?.name || "",
    description: role?.description || "",
    is_leadership: role?.is_leadership || false,
    scope_override: role?.scope_override || "none",
    permissions: role?.permissions || []
  })

  const { data: availablePermissions = {} } = usePermissions()

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
    onClose()
  }

  const handlePermissionChange = (permission, checked) => {
    setFormData(prev => ({
      ...prev,
      permissions: checked
        ? [...prev.permissions, permission]
        : prev.permissions.filter(p => p !== permission)
    }))
  }

  const selectAllInCategory = (category, permissions) => {
    const allSelected = permissions.every(p => formData.permissions.includes(p))
    if (allSelected) {
      // Deselect all in category
      setFormData(prev => ({
        ...prev,
        permissions: prev.permissions.filter(p => !permissions.includes(p))
      }))
    } else {
      // Select all in category
      setFormData(prev => ({
        ...prev,
        permissions: [...new Set([...prev.permissions, ...permissions])]
      }))
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>
              {role ? 'Edit Role' : 'Create Role'}
            </DialogTitle>
            <DialogDescription>
              {role
                ? 'Update the role details and permissions below.'
                : 'Create a new role with specific permissions and access scope.'}
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="basic">Basic Info</TabsTrigger>
              <TabsTrigger value="permissions">Permissions</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-4">
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="name">Role Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., HR Manager, Team Lead, Admin"
                    required
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe the role's responsibilities and scope"
                    rows={3}
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="scope_override">Access Scope</Label>
                  <Select
                    value={formData.scope_override}
                    onValueChange={(value) => setFormData({ ...formData, scope_override: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select access scope" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(scopeOverrideOptions).map(([key, option]) => (
                        <SelectItem key={key} value={key}>
                          <div className="flex flex-col">
                            <span className="font-medium">{option.label}</span>
                            <span className="text-xs text-muted-foreground">{option.description}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="is_leadership"
                    checked={formData.is_leadership}
                    onCheckedChange={(checked) => setFormData({ ...formData, is_leadership: checked })}
                  />
                  <Label htmlFor="is_leadership" className="text-sm">
                    Leadership Role
                    <p className="text-xs text-muted-foreground">
                      Users with this role become leaders of their organizational level
                    </p>
                  </Label>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="permissions" className="space-y-4">
              <div className="py-4">
                <div className="mb-4">
                  <h4 className="text-sm font-medium mb-2">Selected Scope Override:</h4>
                  <Badge className={scopeOverrideOptions[formData.scope_override].color}>
                    {scopeOverrideOptions[formData.scope_override].label}
                  </Badge>
                  <p className="text-xs text-muted-foreground mt-1">
                    {scopeOverrideOptions[formData.scope_override].description}
                  </p>
                </div>

                <Separator className="my-4" />

                <div className="space-y-6">
                  {Object.entries(permissionCategories).map(([category, permissions]) => {
                    const categoryPermissions = permissions.filter(p =>
                      availablePermissions[p] || permissions.includes(p)
                    )
                    const selectedCount = categoryPermissions.filter(p =>
                      formData.permissions.includes(p)
                    ).length
                    const allSelected = selectedCount === categoryPermissions.length

                    return (
                      <div key={category} className="space-y-3">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-sm">{category}</h4>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-muted-foreground">
                              {selectedCount}/{categoryPermissions.length}
                            </span>
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => selectAllInCategory(category, categoryPermissions)}
                            >
                              {allSelected ? 'Deselect All' : 'Select All'}
                            </Button>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 gap-2">
                          {categoryPermissions.map((permission) => (
                            <div key={permission} className="flex items-center space-x-2">
                              <Checkbox
                                id={permission}
                                checked={formData.permissions.includes(permission)}
                                onCheckedChange={(checked) => handlePermissionChange(permission, checked)}
                              />
                              <Label htmlFor={permission} className="text-sm flex-1">
                                {permission.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </Label>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <DialogFooter className="mt-6">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">
              {role ? 'Update Role' : 'Create Role'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
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
            <div className="mt-2 flex flex-wrap gap-1 max-h-32 overflow-y-auto">
              {role.permissions?.map((permission) => (
                <Badge key={permission} variant="outline" className="text-xs">
                  {permission.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </Badge>
              ))}
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