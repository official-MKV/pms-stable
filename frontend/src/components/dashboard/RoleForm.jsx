"use client"

import { useState, useEffect } from "react"
import { AlertCircle, Loader2 } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"

export function RoleForm({ isOpen, onClose, onSubmit, loading = false }) {
  const [formData, setFormData] = useState({
    roleName: "",
    department: "",
    reportingTo: "",
    isLeadership: "no",
    responsibilities: "",
  })

  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!isOpen) {
      resetForm()
      setError(null)
    }
  }, [isOpen])

  const resetForm = () => {
    setFormData({
      roleName: "",
      department: "",
      reportingTo: "",
      isLeadership: "no",
      responsibilities: "",
    })
    setErrors({})
  }

  const validateForm = () => {
    const newErrors = {}
    if (!formData.roleName.trim()) newErrors.roleName = "Role name is required"
    if (!formData.department.trim()) newErrors.department = "Department is required"
    if (!formData.reportingTo.trim()) newErrors.reportingTo = "Reporting to is required"
    if (!formData.responsibilities.trim()) newErrors.responsibilities = "Responsibilities are required"
    return newErrors
  }

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const newErrors = validateForm()

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setSubmitting(true)
    try {
      await onSubmit(formData)
      resetForm()
      onClose()
    } catch (err) {
      const message = err instanceof Error ? err.message : "An error occurred"
      setError(message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[550px] max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit} className="space-y-8">
          <DialogHeader className="space-y-4">
            <DialogTitle className="text-2xl font-bold">Create New Role</DialogTitle>
            <DialogDescription className="text-base">
              Define and manage organizational roles and responsibilities
            </DialogDescription>
          </DialogHeader>

          {error && (
            <Alert variant="destructive" className="flex gap-2">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="grid gap-10">
            {/* Role Information Section */}
            <div className="space-y-5">
              <h3 className="text-sm font-semibold text-foreground">Role Information</h3>
              <div className="grid gap-5">
                <div className="grid gap-3">
                  <Label htmlFor="roleName" className="text-sm font-medium">
                    Role Name *
                  </Label>
                  <Input
                    id="roleName"
                    value={formData.roleName}
                    onChange={(e) => handleChange("roleName", e.target.value)}
                    placeholder="e.g., Senior Developer"
                    disabled={submitting || loading}
                    className={errors.roleName ? "border-destructive" : ""}
                  />
                  {errors.roleName && <p className="text-destructive text-sm">{errors.roleName}</p>}
                </div>

                <div className="grid gap-3">
                  <Label htmlFor="department" className="text-sm font-medium">
                    Department *
                  </Label>
                  <Input
                    id="department"
                    value={formData.department}
                    onChange={(e) => handleChange("department", e.target.value)}
                    placeholder="e.g., Engineering"
                    disabled={submitting || loading}
                    className={errors.department ? "border-destructive" : ""}
                  />
                  {errors.department && <p className="text-destructive text-sm">{errors.department}</p>}
                </div>

                <div className="grid gap-3">
                  <Label htmlFor="reportingTo" className="text-sm font-medium">
                    Reports To *
                  </Label>
                  <Input
                    id="reportingTo"
                    value={formData.reportingTo}
                    onChange={(e) => handleChange("reportingTo", e.target.value)}
                    placeholder="e.g., CTO"
                    disabled={submitting || loading}
                    className={errors.reportingTo ? "border-destructive" : ""}
                  />
                  {errors.reportingTo && <p className="text-destructive text-sm">{errors.reportingTo}</p>}
                </div>
              </div>
            </div>

            {/* Leadership Status Section */}
            <div className="space-y-5">
              <h3 className="text-sm font-semibold text-foreground">Role Type</h3>
              <div className="bg-slate-50 p-6 rounded-lg border border-slate-200 space-y-5">
                <p className="text-sm text-slate-700 font-medium">Is this a leadership role?</p>

                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      id="leadershipYes"
                      name="isLeadership"
                      value="yes"
                      checked={formData.isLeadership === "yes"}
                      onChange={(e) => handleChange("isLeadership", e.target.value)}
                      className="h-4 w-4 cursor-pointer"
                    />
                    <Label htmlFor="leadershipYes" className="cursor-pointer text-base">
                      Yes
                    </Label>
                  </div>

                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      id="leadershipNo"
                      name="isLeadership"
                      value="no"
                      checked={formData.isLeadership === "no"}
                      onChange={(e) => handleChange("isLeadership", e.target.value)}
                      className="h-4 w-4 cursor-pointer"
                    />
                    <Label htmlFor="leadershipNo" className="cursor-pointer text-base">
                      No
                    </Label>
                  </div>
                </div>
              </div>
            </div>

            {/* Responsibilities Section */}
            <div className="space-y-5">
              <Label htmlFor="responsibilities" className="text-sm font-medium">
                Key Responsibilities *
              </Label>
              <textarea
                id="responsibilities"
                value={formData.responsibilities}
                onChange={(e) => handleChange("responsibilities", e.target.value)}
                placeholder="Describe the main responsibilities for this role..."
                rows="5"
                disabled={submitting || loading}
                className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
                  errors.responsibilities ? "border-destructive" : "border-slate-300"
                }`}
              />
              {errors.responsibilities && <p className="text-destructive text-sm mt-2">{errors.responsibilities}</p>}
            </div>
          </div>

          <DialogFooter className="flex gap-2 justify-end pt-8">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={submitting || loading}
              className="px-6 bg-transparent"
            >
              Cancel
            </Button>
            <Button type="submit" disabled={submitting || loading} className="px-6 gap-2">
              {submitting || loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create Role"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default RoleForm
