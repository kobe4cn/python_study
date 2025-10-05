import { UserRole, ROLE_LABELS, ROLE_DESCRIPTIONS } from '@/types'

interface RoleSelectorProps {
  value: UserRole
  onChange: (role: UserRole) => void
  disabled?: boolean
  showDescription?: boolean
}

const ROLE_ICONS = {
  admin: '🛡️',
  editor: '✏️',
  viewer: '👁️',
}

const ROLE_COLORS = {
  admin: 'border-red-300 bg-red-50 hover:bg-red-100',
  editor: 'border-blue-300 bg-blue-50 hover:bg-blue-100',
  viewer: 'border-gray-300 bg-gray-50 hover:bg-gray-100',
}

/**
 * 角色选择器组件 - 可视化的角色选择
 */
export function RoleSelector({
  value,
  onChange,
  disabled = false,
  showDescription = true,
}: RoleSelectorProps) {
  const roles: UserRole[] = ['admin', 'editor', 'viewer']

  return (
    <div className="space-y-3">
      {roles.map((role) => {
        const isSelected = value === role
        return (
          <button
            key={role}
            type="button"
            onClick={() => onChange(role)}
            disabled={disabled}
            className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
              isSelected
                ? 'border-blue-500 bg-blue-50 shadow-md'
                : ROLE_COLORS[role]
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <div className="flex items-start">
              <span className="text-2xl mr-3">{ROLE_ICONS[role]}</span>
              <div className="flex-1">
                <div className="flex items-center">
                  <span className="font-semibold text-gray-900">
                    {ROLE_LABELS[role]}
                  </span>
                  {isSelected && (
                    <span className="ml-2 text-blue-600">✓</span>
                  )}
                </div>
                {showDescription && (
                  <p className="text-sm text-gray-600 mt-1">
                    {ROLE_DESCRIPTIONS[role]}
                  </p>
                )}
              </div>
            </div>
          </button>
        )
      })}
    </div>
  )
}

/**
 * 简单的下拉选择器版本
 */
export function RoleSelect({
  value,
  onChange,
  disabled = false,
}: Omit<RoleSelectorProps, 'showDescription'>) {
  const roles: UserRole[] = ['admin', 'editor', 'viewer']

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as UserRole)}
      disabled={disabled}
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {roles.map((role) => (
        <option key={role} value={role}>
          {ROLE_ICONS[role]} {ROLE_LABELS[role]}
        </option>
      ))}
    </select>
  )
}
