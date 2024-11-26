import { render, screen } from '@testing-library/react'
import { AssistantBuilder } from '../assistant-builder'
import { useRouter } from 'next/navigation'
import { useAssistants } from '@/data-provider/query-service'
import { useSlugRoutes } from '@/hooks/useSlugParams'

jest.mock('../edit-assistant', () => {
  return {
    EditAssistant: jest.fn(() => <div>EditAssistant</div>),
  }
})
jest.mock('../create-assistant', () => {
  return {
    CreateAssistant: jest.fn(() => <div>CreateAssistant</div>),
  }
})

jest.mock('next/navigation', () => {
  return {
    useRouter: jest.fn(),
  }
})

jest.mock('@/data-provider/query-service', () => {
  return {
    useAssistants: jest.fn(),
  }
})

jest.mock('@/hooks/useSlugParams', () => {
  return {
    useSlugRoutes: jest.fn(),
  }
})

test('should render', () => {
  ;(useAssistants as jest.Mock).mockReturnValue({ data: [{ id: '1' }] })
  ;(useRouter as jest.Mock).mockReturnValue([])
  ;(useSlugRoutes as jest.Mock).mockReturnValue({ assistantId: '1' })

  render(<AssistantBuilder />)

  expect(screen.getByText('EditAssistant')).toBeInTheDocument()
  expect(screen.queryByText('CreateAssistant')).toBeNull()
})
