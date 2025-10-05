import { useState, useEffect } from 'react'
import {
  Permission,
  UserRole,
  PERMISSION_LABELS,
  PERMISSION_GROUPS,
  ROLE_PERMISSIONS,
} from '@/types'

interface PermissionEditorProps {
  selectedRole: UserRole
  selectedPermissions: Permission[]
  onChange: (permissions: Permission[]) => void
  disabled?: boolean
}

const GROUP_LABELS = {
  document: '📄 文档权限',
  collection: '📁 集合权限',
  search: '🔍 搜索权限',
  user: '👥 用户权限',
}

/**
 * 权限编辑器组件 - 树形结构的权限选择
 */
export function PermissionEditor({
  selectedRole,
  selectedPermissions,
  onChange,
  disabled = false,
}: PermissionEditorProps) {
  const [permissions, setPermissions] = useState<Permission[]>(selectedPermissions)

  // 当角色改变时，自动设置对应的权限
  useEffect(() => {
    const rolePermissions = ROLE_PERMISSIONS[selectedRole]
    setPermissions(rolePermissions)
    onChange(rolePermissions)
  }, [selectedRole])

  // 同步外部权限变化
  useEffect(() => {
    setPermissions(selectedPermissions)
  }, [selectedPermissions])

  const handleTogglePermission = (permission: Permission) => {
    const newPermissions = permissions.includes(permission)
      ? permissions.filter((p) => p !== permission)
      : [...permissions, permission]

    setPermissions(newPermissions)
    onChange(newPermissions)
  }

  const handleToggleGroup = (groupPermissions: Permission[]) => {
    const allSelected = groupPermissions.every((p) => permissions.includes(p))

    const newPermissions = allSelected
      ? permissions.filter((p) => !groupPermissions.includes(p))
      : [...new Set([...permissions, ...groupPermissions])]

    setPermissions(newPermissions)
    onChange(newPermissions)
  }

  const isGroupSelected = (groupPermissions: Permission[]) => {
    return groupPermissions.every((p) => permissions.includes(p))
  }

  const isGroupPartiallySelected = (groupPermissions: Permission[]) => {
    const selected = groupPermissions.filter((p) => permissions.includes(p))
    return selected.length > 0 && selected.length < groupPermissions.length
  }

  return (
    <div className="space-y-4">
      {/* 预设权限提示 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-sm text-blue-800">
          <span className="font-semibold">当前角色预设权限：</span>
          <br />
          您可以在预设权限基础上自定义权限配置
        </p>
      </div>

      {/* 权限分组 */}
      <div className="space-y-3">
        {Object.entries(PERMISSION_GROUPS).map(([groupKey, groupPermissions]) => {
          const allSelected = isGroupSelected(groupPermissions)
          const partiallySelected = isGroupPartiallySelected(groupPermissions)

          return (
            <div
              key={groupKey}
              className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
            >
              {/* 分组标题 */}
              <div className="flex items-center mb-3">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(el) => {
                    if (el) el.indeterminate = partiallySelected
                  }}
                  onChange={() => handleToggleGroup(groupPermissions)}
                  disabled={disabled}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500 disabled:opacity-50"
                />
                <label className="ml-2 font-semibold text-gray-900">
                  {GROUP_LABELS[groupKey as keyof typeof GROUP_LABELS]}
                </label>
              </div>

              {/* 权限列表 */}
              <div className="ml-6 space-y-2">
                {groupPermissions.map((permission) => (
                  <div key={permission} className="flex items-center">
                    <input
                      type="checkbox"
                      id={permission}
                      checked={permissions.includes(permission)}
                      onChange={() => handleTogglePermission(permission)}
                      disabled={disabled}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500 disabled:opacity-50"
                    />
                    <label
                      htmlFor={permission}
                      className="ml-2 text-sm text-gray-700 cursor-pointer"
                    >
                      <span className="font-mono text-xs text-gray-500 mr-2">
                        {permission}
                      </span>
                      {PERMISSION_LABELS[permission]}
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {/* 已选权限统计 */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
        <p className="text-sm text-gray-700">
          已选择 <span className="font-semibold">{permissions.length}</span> 项权限
        </p>
      </div>
    </div>
  )
}
