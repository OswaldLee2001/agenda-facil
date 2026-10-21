import { useEffect, useState } from 'react'
import ClientPage from './pages/ClientPage'
import './App.css'

type Service = {
  id: number
  name: string
  description: string
  duration_minutes: number
  price_cents: number
  available: boolean
}

type Professional = {
  id: number
  name: string
  email: string
  phone: string
  available: boolean
}

type WorkingHours = {
  weekday: number
  start_time: string
  end_time: string
}

type Appointment = {
	id: number
	professional_id: number
	service_id: number
	client_name: string
	client_phone: string
	appointment_date: string
	appointment_time: string
	status: string
	professional: {
		id: number
		name: string
	}
	service: {
		id: number
		name: string
	}
}

type AuthMode = 'login' | 'register'

type AuthResponse = {
  access_token: string
  token_type: string
}

const API_URL = 'http://localhost:8000'

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
})

function App() {
  const [services, setServices] = useState<Service[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [selectedServiceId, setSelectedServiceId] = useState<number | null>(
    null,
  )

  const [professionals, setProfessionals] = useState<Professional[]>([])
  const [professionalsLoading, setProfessionalsLoading] = useState(true)
  const [professionalsError, setProfessionalsError] = useState<string | null>(
    null,
  )

  const [selectedProfessionalId, setSelectedProfessionalId] = useState<
    number | null
  >(null)

  const [authMode, setAuthMode] = useState<AuthMode>('register')
  const [currentPage, setCurrentPage] = useState<'home' | 'client'>('home')
  const [authToken, setAuthToken] = useState<string | null>(null)
  const [authUserName, setAuthUserName] = useState('')
  const [authName, setAuthName] = useState('')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [authBusy, setAuthBusy] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)
  const [authSuccess, setAuthSuccess] = useState<string | null>(null)

  const [appointmentClientName, setAppointmentClientName] = useState('')
  const [appointmentClientPhone, setAppointmentClientPhone] = useState('')
  const [appointmentDate, setAppointmentDate] = useState('')
  const [appointmentTime, setAppointmentTime] = useState('')

  const [availableSlots, setAvailableSlots] = useState<string[]>([])
  const [availableSlotsLoading, setAvailableSlotsLoading] = useState(false)
  const [availableSlotsError, setAvailableSlotsError] = useState<string | null>(
    null,
  )
  const [slotsRefreshKey, setSlotsRefreshKey] = useState(0)

  const [professionalWorkingHours, setProfessionalWorkingHours] = useState<
    WorkingHours[]
  >([])
  const [professionalWorkingHoursLoading, setProfessionalWorkingHoursLoading] =
    useState(false)

  const [appointmentBusy, setAppointmentBusy] = useState(false)
  const [appointmentError, setAppointmentsError] = useState<string | null>(null)
  const [appointmentSuccess, setAppointmentSuccess] = useState<string | null>(
    null,
  )
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [appointmentsLoading, setAppointmentsLoading] = useState(false)
  const [appointmentsError, setAppointmentError] = useState<string | null>(null)
  const [appointmentsRefreshKey, setAppointmentsRefreshKey] = useState(0)

  const selectedService = services.find(
    (service) => service.id === selectedServiceId,
  )

  const selectedProfessional = professionals.find(
    (professional) => professional.id === selectedProfessionalId,
  )

  const now = new Date()
  const minAppointmentDate = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, '0'),
    String(now.getDate()).padStart(2, '0'),
  ].join('-')

  // Carrega os serviços disponíveis.
  useEffect(() => {
    const controller = new AbortController()

    async function loadServices() {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(`${API_URL}/services/`, {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error(`Erro HTTP ${response.status}`)
        }

        const data: Service[] = await response.json()

        setServices(data.filter((service) => service.available))
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          return
        }

        setError(
          'Não foi possível carregar os serviços. Tente novamente mais tarde.',
        )
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    void loadServices()

    return () => controller.abort()
  }, [])

  // Carrega os agendamentos do usuário autenticado.
  useEffect(() => {
    const controller = new AbortController()

    async function loadAppointments() {
      if (!authToken) {
        setAppointments([])
        setAppointmentsError(null)
        setAppointmentsLoading(false)
        return
      }

      try {
        setAppointmentsLoading(true)
        setAppointmentsError(null)

        const response = await fetch(`${API_URL}/appointments/`, {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error(`Erro HTTP ${response.status}`)
        }

        const data: Appointment[] = await response.json()
        setAppointments(data)
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          return
        }

        setAppointmentsError(
          'Não foi possível carregar seus agendamentos. Tente novamente.',
        )
      } finally {
        if (!controller.signal.aborted) {
          setAppointmentsLoading(false)
        }
      }
    }

    void loadAppointments()

    return () => {
      controller.abort()
    }
  }, [authToken, appointmentsRefreshKey])

  // Carrega os profissionais disponíveis.
  useEffect(() => {
    const controller = new AbortController()

    async function loadProfessionals() {
      try {
        setProfessionalsLoading(true)
        setProfessionalsError(null)

        const response = await fetch(`${API_URL}/professionals/`, {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error(`Erro HTTP ${response.status}`)
        }

        const data: Professional[] = await response.json()

        setProfessionals(
          data.filter((professional) => professional.available),
        )
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          return
        }

        setProfessionalsError(
          'Não foi possível carregar os profissionais. Tente novamente mais tarde.',
        )
      } finally {
        if (!controller.signal.aborted) {
          setProfessionalsLoading(false)
        }
      }
    }

    void loadProfessionals()

    return () => controller.abort()
  }, [])

  // Carrega os horários de funcionamento do profissional selecionado.
  useEffect(() => {
    if (selectedProfessionalId === null) {
      setProfessionalWorkingHours([])
      setProfessionalWorkingHoursLoading(false)
      return
    }

    const controller = new AbortController()

    async function loadProfessionalWorkingHours() {
      setProfessionalWorkingHours([])
      setProfessionalWorkingHoursLoading(true)

      try {
        const response = await fetch(
          `${API_URL}/professionals/${selectedProfessionalId}/working-hours/`,
          { signal: controller.signal },
        )

        if (!response.ok) {
          throw new Error(
            'Não foi possível carregar os horários do profissional.',
          )
        }

        const data: WorkingHours[] = await response.json()
        setProfessionalWorkingHours(data)
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          return
        }

        setProfessionalWorkingHours([])
        console.error('Erro ao carregar horários:', err)
      } finally {
        if (!controller.signal.aborted) {
          setProfessionalWorkingHoursLoading(false)
        }
      }
    }

    void loadProfessionalWorkingHours()

    return () => controller.abort()
  }, [selectedProfessionalId])

  // Consulta os horários disponíveis para o serviço, profissional e data.
  useEffect(() => {
    if (
      selectedProfessionalId === null ||
      selectedServiceId === null ||
      !appointmentDate
    ) {
      setAvailableSlots([])
      setAvailableSlotsLoading(false)
      setAvailableSlotsError(null)
      setAppointmentTime('')
      return
    }

    const controller = new AbortController()

    async function loadAvailableSlots() {
      setAvailableSlots([])
      setAvailableSlotsLoading(true)
      setAvailableSlotsError(null)
      setAppointmentTime('')

      try {
        const params = new URLSearchParams({
          appointment_date: appointmentDate,
          service_id: String(selectedServiceId),
        })

        const response = await fetch(
          `${API_URL}/professionals/${selectedProfessionalId}/available-slots/?${params.toString()}`,
          { signal: controller.signal },
        )

        if (!response.ok) {
          throw new Error(
            'Não foi possível consultar os horários disponíveis.',
          )
        }

        const data: string[] = await response.json()
        setAvailableSlots(data)
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          return
        }

        setAvailableSlotsError(
          err instanceof Error
            ? err.message
            : 'Ocorreu um erro ao consultar os horários.',
        )
      } finally {
        if (!controller.signal.aborted) {
          setAvailableSlotsLoading(false)
        }
      }
    }

    void loadAvailableSlots()

    return () => controller.abort()
  }, [selectedProfessionalId, selectedServiceId, appointmentDate, slotsRefreshKey,])

  // Cadastro e login.
  async function handleAuthSubmit() {
    setAuthBusy(true)
    setAuthError(null)
    setAuthSuccess(null)

    try {
      if (authMode === 'register') {
        const registerResponse = await fetch(`${API_URL}/users/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: authName.trim(),
            email: authEmail.trim(),
            password: authPassword,
          }),
        })

        if (!registerResponse.ok) {
          const errorData = await registerResponse
            .json()
            .catch(() => null)

          const detail = errorData?.detail
          const message =
            typeof detail === 'string'
              ? detail
              : 'Não foi possível criar a conta. Confira os dados informados.'

          throw new Error(message)
        }
      }

      const loginResponse = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: authEmail.trim(),
          password: authPassword,
        }),
      })

      if (!loginResponse.ok) {
        const errorData = await loginResponse.json().catch(() => null)
        const detail = errorData?.detail

        const message =
          typeof detail === 'string'
            ? detail
            : authMode === 'register'
              ? 'Conta criada, mas não foi possível entrar automaticamente. Tente fazer login.'
              : 'E-mail ou senha incorretos.'

        throw new Error(message)
      }

      const data: AuthResponse = await loginResponse.json()

      setAuthToken(data.access_token)
      setAuthUserName(
        authMode === 'register' ? authName.trim() : authEmail.trim(),
      )
      setAuthPassword('')
      setAuthSuccess(
        authMode === 'register'
          ? 'Conta criada e login realizado com sucesso!'
          : 'Login realizado com sucesso!',
      )
    } catch (err) {
      setAuthError(
        err instanceof Error
          ? err.message
          : 'Ocorreu um erro inesperado. Tente novamente.',
      )
    } finally {
      setAuthBusy(false)
    }
  }

  // Envia o agendamento para o backend.
  async function handleAppointmentSubmit() {
    if (!authToken) {
      setAppointmentError('Entre na sua conta antes de agendar.')
      return
    }

    if (!selectedService || !selectedProfessional) {
      setAppointmentError('Selecione um serviço e um profissional.')
      return
    }

    if (
      !appointmentClientName.trim() ||
      !appointmentClientPhone.trim() ||
      !appointmentDate ||
      !appointmentTime
    ) {
      setAppointmentError('Preencha todos os campos do agendamento.')
      return
    }

    if (professionalWorkingHoursLoading || availableSlotsLoading) {
      setAppointmentError(
        'Aguarde o carregamento dos horários antes de continuar.',
      )
      return
    }

    if (availableSlotsError) {
      setAppointmentError(
        'Não foi possível consultar os horários. Selecione novamente a data para tentar outra vez.',
      )
      return
    }

    if (!availableSlots.includes(appointmentTime)) {
      setAppointmentError(
        'O horário selecionado não está mais disponível. Escolha outro horário.',
      )
      setAppointmentTime('')
      return
    }

    if (professionalWorkingHours.length === 0) {
      setAppointmentError(
        'Este profissional não possui horários cadastrados para agendamento.',
      )
      return
    }

    const [year, month, day] = appointmentDate.split('-').map(Number)
    const selectedDate = new Date(year, month - 1, day)
    const weekday = (selectedDate.getDay() + 6) % 7

    const worksOnSelectedDay = professionalWorkingHours.some(
      (hours) => hours.weekday === weekday,
    )

    if (!worksOnSelectedDay) {
      setAppointmentError('O profissional não trabalha nesse dia.')
      return
    }

    setAppointmentBusy(true)
    setAppointmentError(null)
    setAppointmentSuccess(null)

    try {
      const response = await fetch(`${API_URL}/appointments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          professional_id: selectedProfessional.id,
          service_id: selectedService.id,
          client_name: appointmentClientName.trim(),
          client_phone: appointmentClientPhone.trim(),
          appointment_date: appointmentDate,
          appointment_time: appointmentTime,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        const detail = errorData?.detail

        const message =
          typeof detail === 'string'
            ? detail
            : 'Não foi possível realizar o agendamento. Confira os dados e tente outro horário.'

        throw new Error(message)
      }

      setAppointmentSuccess('Agendamento realizado com sucesso!')
      setAppointmentTime('')
	  setSlotsRefreshKey((currentKey) => currentKey + 1)
	  setAppointmentsRefreshKey((currentKey) => currentKey + 1)
    } catch (err) {
      setAppointmentError(
        err instanceof Error
          ? err.message
          : 'Ocorreu um erro inesperado ao realizar o agendamento.',
      )
    } finally {
      setAppointmentBusy(false)
    }
  }

  // Atualiza a data escolhida e reinicia a seleção de horário.
  function handleAppointmentDateChange(date: string) {
	setAppointmentError(null)
	setAppointmentSuccess(null)
	setAppointmentTime('')
	setAvailableSlots([])
	setAvailableSlotsError(null)
	setAppointmentDate(date)
  }

  async function handleCancelAppointment(appointmentId: number) {
    const appointment = appointments.find(
      (item) => item.id === appointmentId,
    )

    if (!appointment || !authToken) {
      return
    }

    try {
      const response = await fetch(
        `${API_URL}/appointments/${appointmentId}`,
        {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            professional_id: appointment.professional_id,
            service_id: appointment.service_id,
            client_name: appointment.client_name,
            client_phone: appointment.client_phone,
            appointment_date: appointment.appointment_date,
            appointment_time: appointment.appointment_time,
            status: 'cancelled',
          }),
        },
      )

      if (!response.ok) {
        throw new Error('Não foi possível cancelar o agendamento.')
      }

      setAppointmentsRefreshKey((currentKey) => currentKey + 1)
    } catch (err) {
      console.error('Erro ao cancelar agendamento:', err)
      window.alert(
        err instanceof Error
          ? err.message
          : 'Ocorreu um erro inesperado ao cancelar o agendamento.',
      )
    }
  }

  // Valida a data escolhida.
  if (currentPage === 'client' && authToken) {
	return (
		<ClientPage
			appointments={appointments}
			appointmentsLoading={appointmentsLoading}
			appointmentsError={appointmentsError}
			onCancelAppointment={handleCancelAppointment}
			onGoHome={() => setCurrentPage('home')}
		/>
	)
}


  return (
    <main className="booking-page">
      <header className="site-header">
        <a className="brand" href="/">
          <span className="brand-icon">A</span>
          <span>Agenda Fácil</span>
        </a>


	 <nav aria-label="Navegação principal">
          {currentPage === 'home' ? (
            <>
              <a href="#servicos">Serviços</a>
              <a href="#profissionais">Profissionais</a>
              <a href="#como-funciona">Como funciona</a>
              <a href="#conta">Minha conta</a>

              {authToken && (
                <a
                  href="#area-do-cliente"
                  onClick={(event) => {
                    event.preventDefault()
                    setCurrentPage('client')
                  }}
                >
                  Área do cliente
                </a>
              )}
            </>
          ) : (
            <a
              href="#inicio"
              onClick={(event) => {
                event.preventDefault()
                setCurrentPage('home')
              }}
            >
              Página inicial
            </a>
          )}
		</nav>
      </header>

      <section className="booking-hero">
        <span className="eyebrow">AGENDAMENTO ONLINE</span>

        <h1>
          Seu próximo horário,
          <br />
          <span>sem complicação.</span>
        </h1>

        <p>
          Escolha seu serviço, encontre um profissional e reserve o horário
          ideal para você.
        </p>

        <a className="primary-button" href="#servicos">
          Encontrar um serviço
        </a>
      </section>

      <section id="conta" className="services-section">
        <div className="section-heading">
          <span className="eyebrow">SUA CONTA</span>

          <h2>
            {authToken
              ? `Olá, ${authUserName}!`
              : authMode === 'register'
                ? 'Crie sua conta'
                : 'Entre na sua conta'}
          </h2>

          <p>
            {authToken
              ? 'Você já está autenticado e pode continuar seu agendamento.'
              : 'Entre ou cadastre-se para continuar com seu agendamento.'}
          </p>
        </div>

        {!authToken && (
          <form
            className="auth-form"
            onSubmit={(event) => {
              event.preventDefault()
              void handleAuthSubmit()
            }}
          >
            <div className="auth-mode-switch">
              <button
                type="button"
                className={
                  authMode === 'register' ? 'primary-button' : 'retry-button'
                }
                onClick={() => {
                  setAuthMode('register')
                  setAuthError(null)
                  setAuthSuccess(null)
                }}
              >
                Criar conta
              </button>

              <button
                type="button"
                className={
                  authMode === 'login' ? 'primary-button' : 'retry-button'
                }
                onClick={() => {
                  setAuthMode('login')
                  setAuthError(null)
                  setAuthSuccess(null)
                }}
              >
                Já tenho conta
              </button>
            </div>

            {authMode === 'register' && (
              <label className="auth-field">
                Nome completo
                <input
                  type="text"
                  autoComplete="name"
                  value={authName}
                  onChange={(event) => setAuthName(event.target.value)}
                  required
                  minLength={2}
                  maxLength={120}
                  placeholder="Seu nome"
                />
              </label>
            )}

            <label className="auth-field">
              E-mail
              <input
                type="email"
                autoComplete="email"
                value={authEmail}
                onChange={(event) => setAuthEmail(event.target.value)}
                required
                maxLength={254}
                placeholder="voce@exemplo.com"
              />
            </label>

            <label className="auth-field">
              Senha
              <input
                type="password"
                autoComplete={
                  authMode === 'register' ? 'new-password' : 'current-password'
                }
                value={authPassword}
                onChange={(event) => setAuthPassword(event.target.value)}
                required
                minLength={8}
                maxLength={128}
                placeholder="Pelo menos 8 caracteres"
              />
            </label>

            {authError && (
              <p className="error-message" role="alert">
                {authError}
              </p>
            )}

            {authSuccess && (
              <p className="success-message" role="status">
                {authSuccess}
              </p>
            )}

            <button
              className="primary-button"
              type="submit"
              disabled={authBusy}
            >
              {authBusy
                ? 'Aguarde...'
                : authMode === 'register'
                  ? 'Criar conta e entrar'
                  : 'Entrar'}
            </button>
          </form>
        )}

        {authToken && (
          <div className="selected-service-summary">
            <p>{authSuccess || 'Login realizado com sucesso.'}</p>

            <button
              className="retry-button"
              type="button"
              onClick={() => {
                setAuthToken(null)
                setAuthUserName('')
                setAuthSuccess(null)
                setAuthError(null)
              }}
            >
              Sair da conta
            </button>
          </div>
        )}
      </section>

      <section id="servicos" className="services-section">
        <div className="section-heading">
          <span className="eyebrow">ETAPA 1</span>
          <h2>Como podemos ajudar?</h2>
          <p>Escolha um dos serviços disponíveis.</p>
        </div>

        {loading && (
          <p className="services-message" role="status">
            Carregando serviços...
          </p>
        )}

        {error && (
          <div className="services-message error-message" role="alert">
            <p>{error}</p>

            <button
              className="retry-button"
              type="button"
              onClick={() => window.location.reload()}
            >
              Tentar novamente
            </button>
          </div>
        )}

        {!loading && !error && services.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-icon" aria-hidden="true">
              <span>＋</span>
            </div>

            <h3>Nenhum serviço disponível no momento</h3>

            <p>
              Volte mais tarde para conferir as opções de agendamento.
            </p>
          </div>
        )}

        {!loading && !error && services.length > 0 && (
          <div className="services-grid">
            {services.map((service) => (
              <article
                className={`service-card ${
                  selectedServiceId === service.id
                    ? 'service-card-selected'
                    : ''
                }`}
                key={service.id}
              >
                <span className="service-status">Disponível</span>

                <h3>{service.name}</h3>

                <p className="service-description">
                  {service.description ||
                    'Consulte os detalhes deste serviço.'}
                </p>

                <div className="service-details">
                  <span>
                    <span aria-hidden="true">◷</span>{' '}
                    {service.duration_minutes} min
                  </span>

                  <strong>
                    {currencyFormatter.format(service.price_cents / 100)}
                  </strong>
                </div>

                <button
                  className="select-service-button"
                  type="button"
                  onClick={() => {
                    setSelectedServiceId(service.id)
                    setSelectedProfessionalId(null)
                    setAppointmentDate('')
                    setAppointmentTime('')
                    setAvailableSlots([])
                    setAvailableSlotsError(null)
                    setAppointmentError(null)
                    setAppointmentSuccess(null)
                  }}
                  aria-pressed={selectedServiceId === service.id}
                >
                  {selectedServiceId === service.id
                    ? 'Serviço selecionado'
                    : 'Escolher serviço'}
                </button>
              </article>
            ))}
          </div>
        )}

        {!loading && !error && selectedService && (
          <section className="selected-service-summary" aria-live="polite">
            <span className="eyebrow">SUA ESCOLHA</span>

            <h3>{selectedService.name}</h3>

            <p>Duração: {selectedService.duration_minutes} minutos</p>

            <p>
              Valor:{' '}
              {currencyFormatter.format(selectedService.price_cents / 100)}
            </p>
          </section>
        )}

        {selectedService && (
          <section id="profissionais" className="professionals-section">
            <div className="section-heading">
              <span className="eyebrow">ETAPA 2</span>
              <h2>Escolha seu profissional</h2>
              <p>Selecione quem realizará o serviço escolhido.</p>
            </div>

            {professionalsLoading && (
              <p className="services-message" role="status">
                Carregando profissionais...
              </p>
            )}

            {professionalsError && (
              <div className="services-message error-message" role="alert">
                <p>{professionalsError}</p>

                <button
                  className="retry-button"
                  type="button"
                  onClick={() => window.location.reload()}
                >
                  Tentar novamente
                </button>
              </div>
            )}

            {!professionalsLoading &&
              !professionalsError &&
              professionals.length === 0 && (
                <div className="empty-state">
                  <h3>Nenhum profissional disponível</h3>
                  <p>Volte mais tarde para conferir as opções.</p>
                </div>
              )}

            {!professionalsLoading &&
              !professionalsError &&
              professionals.length > 0 && (
                <div className="services-grid">
                  {professionals.map((professional) => (
                    <article
                      className={`service-card ${
                        selectedProfessionalId === professional.id
                          ? 'service-card-selected'
                          : ''
                      }`}
                      key={professional.id}
                    >
                      <span className="service-status">Disponível</span>

                      <h3>{professional.name}</h3>

                      <p className="service-description">
                        Consulte os horários disponíveis deste profissional.
                      </p>

                      <div className="service-details">
                        <span>{professional.phone}</span>
                      </div>

                      <button
                        className="select-service-button"
                        type="button"
                        onClick={() => {
                          setSelectedProfessionalId(professional.id)
                          setAppointmentDate('')
                          setAppointmentTime('')
                          setAvailableSlots([])
                          setAvailableSlotsError(null)
                          setAppointmentError(null)
                          setAppointmentSuccess(null)
                        }}
                        aria-pressed={
                          selectedProfessionalId === professional.id
                        }
                      >
                        {selectedProfessionalId === professional.id
                          ? 'Profissional selecionado'
                          : 'Escolher profissional'}
                      </button>
                    </article>
                  ))}
                </div>
              )}

            {!professionalsLoading &&
              !professionalsError &&
              selectedProfessional && (
                <section
                  className="selected-service-summary"
                  aria-live="polite"
                >
                  <span className="eyebrow">SUA ESCOLHA</span>

                  <h3>{selectedProfessional.name}</h3>

                  <p>Telefone: {selectedProfessional.phone}</p>
                </section>
              )}

            {selectedProfessional && selectedService && (
              <section className="selected-service-summary">
                <div className="section-heading">
                  <span className="eyebrow">ETAPA 3</span>
                  <h2>Confirme seu agendamento</h2>
                  <p>
                    Preencha seus dados e escolha a data e o horário.
                  </p>
                </div>

                {professionalWorkingHoursLoading && (
                  <p className="services-message" role="status">
                    Carregando os horários do profissional...
                  </p>
                )}

                {!authToken && (
                  <p className="services-message" role="status">
                    Entre ou crie sua conta na seção Minha conta antes de
                    confirmar seu agendamento.
                  </p>
                )}

                {appointmentError && (
                  <p className="error-message" role="alert">
                    {appointmentError}
                  </p>
                )}

                {appointmentSuccess && (
                  <p className="services-message" role="status">
                    {appointmentSuccess}
                  </p>
                )}

                <form
                  className="auth-form"
                  onSubmit={(event) => {
                    event.preventDefault()
                    void handleAppointmentSubmit()
                  }}
                >
                  <label className="auth-field">
                    Nome completo
                    <input
                      type="text"
                      value={appointmentClientName}
                      onChange={(event) =>
                        setAppointmentClientName(event.target.value)
                      }
                      autoComplete="name"
                      required
                      maxLength={100}
                      placeholder="Seu nome completo"
                    />
                  </label>

                  <label className="auth-field">
                    Telefone
                    <input
                      type="tel"
                      value={appointmentClientPhone}
                      onChange={(event) =>
                        setAppointmentClientPhone(event.target.value)
                      }
                      autoComplete="tel"
                      required
                      maxLength={20}
                      placeholder="Seu telefone"
                    />
                  </label>

                  <label className="auth-field">
                    Data
                    <input
                      type="date"
                      value={appointmentDate}
                      min={minAppointmentDate}
                      onChange={(event) =>
                        handleAppointmentDateChange(event.target.value)
                      }
                      disabled={professionalWorkingHoursLoading}
                      required
                    />
                  </label>

                  <label className="auth-field">
                    Horário
                    <select
                      value={appointmentTime}
                      onChange={(event) => {
                        setAppointmentTime(event.target.value)
                        setAppointmentError(null)
                        setAppointmentSuccess(null)
                      }}
                      disabled={
                        !appointmentDate ||
                        professionalWorkingHoursLoading ||
                        availableSlotsLoading ||
                        availableSlots.length === 0
                      }
                      required
                    >
                      <option value="">
                        {!appointmentDate
                          ? 'Selecione uma data primeiro'
                          : availableSlotsLoading
                            ? 'Consultando horários...'
                            : availableSlotsError
                              ? 'Erro ao carregar horários'
                              : availableSlots.length === 0
                                ? 'Nenhum horário disponível'
                                : 'Selecione um horário'}
                      </option>

                      {availableSlots.map((slot) => (
                        <option key={slot} value={slot}>
                          {slot}
                        </option>
                      ))}
                    </select>
                  </label>

                  {availableSlotsError && (
                    <p className="error-message" role="alert">
                      {availableSlotsError}
                    </p>
                  )}

                  {appointmentDate &&
                    !availableSlotsLoading &&
                    !availableSlotsError &&
                    availableSlots.length === 0 && (
                      <p className="services-message" role="status">
                        Não há horários disponíveis para esta data. Tente outro
                        dia.
                      </p>
                    )}

                  <button
                    className="select-service-button"
                    type="submit"
                    disabled={
                      appointmentBusy ||
                      !authToken ||
                      professionalWorkingHoursLoading ||
                      availableSlotsLoading ||
                      Boolean(availableSlotsError) ||
                      !availableSlots.includes(appointmentTime)
                    }
                  >
                    {appointmentBusy
                      ? 'Enviando agendamento...'
                      : 'Confirmar agendamento'}
                  </button>
                </form>
              </section>
            )}
          </section>
        )}
      </section>



      <section id="como-funciona" className="steps-section">
        <h2>Agendar em três passos</h2>

        <div className="steps-grid">
          <article className="step-card">
            <span className="step-number">01</span>
            <h3>Escolha o serviço</h3>
            <p>Encontre o serviço ideal para você.</p>
          </article>

          <article className="step-card">
            <span className="step-number">02</span>
            <h3>Selecione o horário</h3>
            <p>Consulte as opções disponíveis.</p>
          </article>

          <article className="step-card">
            <span className="step-number">03</span>
            <h3>Confirme seu horário</h3>
            <p>Revise os detalhes do agendamento.</p>
          </article>
        </div>
      </section>

      <footer className="site-footer">
        <span>Agenda Fácil</span>
        <span>Seu tempo merece organização.</span>
      </footer>
    </main>
  )
}

export default App
