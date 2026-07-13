import { createBrowserRouter } from 'react-router-dom'
import App from '../App'
import DashboardPage from '../pages/DashboardPage'
import RecordsPage from '../pages/RecordsPage'
import RecordDetailsPage from '../pages/RecordDetailsPage'
import CreateRecordPage from '../pages/CreateRecordPage'
import EditRecordPage from '../pages/EditRecordPage'
import SearchPage from '../pages/SearchPage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'records', element: <RecordsPage /> },
      { path: 'records/new', element: <CreateRecordPage /> },
      { path: 'records/:id', element: <RecordDetailsPage /> },
      { path: 'records/:id/edit', element: <EditRecordPage /> },
      { path: 'search', element: <SearchPage /> },
    ],
  },
])

export default router
