"use client"

import { useState, useEffect } from "react"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { usePermissions } from "@/lib/react-query"

// Scope override options with descriptions
const scopeOverrideOptions = {
  none: {
    label: "No Override",
    description: "Use organizational scope only - access limited to user's organizational unit",
    color: "bg-gray-100 text-gray-800",
  },
  global: {
    label: "Global Access",
    description: "Access all organizational data regardless of position (e.g., HR, Admin)",
    color: "bg-blue-100 text-blue-800",
  },
  cross_directorate: {
    label: "Cross Directorate",
    description: "Access data across multiple directorates within the organization",
    color: "bg-purple-100 text-purple-800",
  },
}

// Helper to format permission names for display
const formatPermissionName = (permission) => {
  if (!permission) return ""
  return permission
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

export function RoleForm({ role, isOpen, onClose, onSubmit }) {
  const { data: permissionGroups = {}, isLoading: permissionsLoading } = usePermissions()

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    is_leadership: false,
    scope_override: "none",
    permissions: [],
  })

  const [submitting, setSubmitting] = useState(false)

  // Update form data when role changes (for editing)
  useEffect(() => {
    if (role) {
      setFormData({
        name: role.name || "",
        description: role.description || "",
        is_leadership: role.is_leadership || false,
        scope_override: role.scope_override || "none",
        permissions: role.permissions || [],
      })
    } else {
      setFormData({
        name: "",
        description: "",
        is_leadership: false,
        scope_override: "none",
        permissions: [],
      })
    }
  }, [role, isOpen])

  // Handle permission checkbox change
  const handlePermissionChange = (permission, checked) => {
    setFormData((prev) => ({
      ...prev,
      permissions: checked
        ? [...prev.permissions, permission]
        : prev.permissions.filter((p) => p !== permission),
    }))
  }

  // Select/deselect all permissions in a category
  const selectAllInCategory = (categoryPermissions) => {
    const allSelected = categoryPermissions.every((p) => formData.permissions.includes(p))

    if (allSelected) {
      // Deselect all in this category
      setFormData((prev) => ({
        ...prev,
        permissions: prev.permissions.filter((p) => !categoryPermissions.includes(p)),
      }))
    } else {
      // Select all in this category
      setFormData((prev) => ({
        ...prev,
        permissions: [...new Set([...prev.permissions, ...categoryPermissions])],
      }))
    }
  }

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.name.trim()) {
      return
    }

    setSubmitting(true)
    try {
      await onSubmit(formData)
      onClose()
    } catch (error) {
      console.error("Error submitting role:", error)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{role ? "Edit Role" : "Create Role"}</DialogTitle>
            <DialogDescription>
              {role
                ? "Update the role details and permissions below."
                : "Create a new role with specific permissions and access scope."}
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="basic">Basic Info</TabsTrigger>
              <TabsTrigger value="permissions">Permissions</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-6 py-4">
              <div className="grid gap-6">
                {/* Role Name */}
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-sm font-semibold">
                    Role Name *
                  </Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., HR Manager, Team Lead, Admin"
                    required
                    disabled={submitting}
                    className="h-10"
                  />
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description" className="text-sm font-semibold">
                    Description
                  </Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe the role's responsibilities and scope"
                    rows={3}
                    disabled={submitting}
                    className="resize-none"
                  />
                </div>

                {/* Access Scope */}
                <div className="space-y-3">
                  <Label className="text-sm font-semibold">Access Scope</Label>
                  <div className="space-y-2">
                    {Object.entries(scopeOverrideOptions).map(([key, option]) => (
                      <div
                        key={key}
                        className={`relative flex items-start space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-slate-50 transition-colors ${
                          formData.scope_override === key ? "border-primary bg-primary/5" : ""
                        }`}
                        onClick={() => !submitting && setFormData({ ...formData, scope_override: key })}
                      >
                        <input
                          type="radio"
                          name="scope_override"
                          value={key}
                          checked={formData.scope_override === key}
                          onChange={() => setFormData({ ...formData, scope_override: key })}
                          disabled={submitting}
                          className="mt-1"
                        />
                        <div className="flex-1">
                          <label className="text-sm font-medium cursor-pointer block">{option.label}</label>
                          <p className="text-xs text-muted-foreground mt-0.5">{option.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Leadership Role */}
                <div className="space-y-3 p-4 border rounded-lg bg-blue-50">
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="is_leadership"
                      checked={formData.is_leadership}
                      onCheckedChange={(checked) => setFormData({ ...formData, is_leadership: !!checked })}
                      disabled={submitting}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <Label htmlFor="is_leadership" className="text-sm font-semibold cursor-pointer block">
                        Leadership Role
                      </Label>
                      <p className="text-xs text-muted-foreground mt-1">
                        Users with this role become leaders of their organizational level
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="permissions" className="space-y-5 py-4">
              <div className="space-y-5">
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold">Selected Scope Override:</h4>
                  <Badge className={scopeOverrideOptions[formData.scope_override]?.color || "bg-gray-100"}>
                    {scopeOverrideOptions[formData.scope_override]?.label || "Unknown"}
                  </Badge>
                  <p className="text-xs text-muted-foreground">
                    {scopeOverrideOptions[formData.scope_override]?.description || ""}
                  </p>
                </div>

                <Separator />

                {permissionsLoading ? (
                  <div className="space-y-4">
                    <Skeleton className="h-20 w-full" />
                    <Skeleton className="h-20 w-full" />
                    <Skeleton className="h-20 w-full" />
                  </div>
                ) : Object.keys(permissionGroups).length > 0 ? (
                  <div className="space-y-5">
                    {Object.entries(permissionGroups).map(([groupKey, groupData]) => {
                      const categoryPermissions = groupData.permissions || []
                      const selectedCount = categoryPermissions.filter((p) =>
                        formData.permissions.includes(p)
                      ).length
                      const allSelected =
                        selectedCount === categoryPermissions.length && categoryPermissions.length > 0

                      return (
                        <div key={groupKey} className="space-y-3 p-4 border rounded-lg bg-slate-50">
                          <div className="flex items-center justify-between gap-4">
                            <div className="flex-1">
                              <h4 className="font-semibold text-sm">{groupData.name || groupKey}</h4>
                              {groupData.description && (
                                <p className="text-xs text-muted-foreground mt-1">{groupData.description}</p>
                              )}
                            </div>
                            <div className="flex items-center gap-2 flex-shrink-0">
                              <span className="text-xs text-muted-foreground whitespace-nowrap">
                                {selectedCount}/{categoryPermissions.length}
                              </span>
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                disabled={submitting}
                                onClick={() => selectAllInCategory(categoryPermissions)}
                              >
                                {allSelected ? "Deselect All" : "Select All"}
                              </Button>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 gap-2">
                            {categoryPermissions.map((permission) => (
                              <div
                                key={permission}
                                className={`flex items-center space-x-3 p-3 bg-white rounded border hover:border-slate-300 transition-colors ${
                                  formData.permissions.includes(permission) ? "border-primary bg-primary/5" : ""
                                }`}
                              >
                                <Checkbox
                                  id={permission}
                                  checked={formData.permissions.includes(permission)}
                                  onCheckedChange={(checked) => handlePermissionChange(permission, !!checked)}
                                  disabled={submitting}
                                />
                                <Label htmlFor={permission} className="text-sm flex-1 cursor-pointer">
                                  {formatPermissionName(permission)}
                                </Label>
                              </div>
                            ))}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>No permissions available</p>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>

          <DialogFooter className="mt-8 flex gap-3 justify-end">
            <Button type="button" variant="outline" onClick={onClose} disabled={submitting}>
              Cancel
            </Button>
            <Button type="submit" disabled={submitting || !formData.name.trim()}>
              {submitting ? (role ? "Updating..." : "Creating...") : role ? "Update Role" : "Create Role"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default RoleForm
