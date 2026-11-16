import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login';
import { DashboardComponent } from './components/dashboard/dashboard';
import { ListaLotesComponent } from './components/lista-lotes/lista-lotes';
import { DetalleLoteComponent } from './components/detalle-lote/detalle-lote';
import { CrearLoteComponent } from './components/crear-lote/crear-lote';
import { TrazabilidadPublicaComponent } from './components/trazabilidad-publica/trazabilidad-publica';
import { ListaFincasComponent } from './components/lista-fincas/lista-fincas';
import { LandingComponent } from './components/landing/landing';
import { RegistroComponent } from './components/registro/registro';
import { CrearFincaComponent } from './components/crear-finca/crear-finca';
import { AdminPanelComponent } from './components/admin-panel/admin-panel';
import { ResumenComponent } from './components/resumen/resumen';
import { ProximamenteComponent } from './components/proximamente/proximamente';


export const routes: Routes = [
  { path: '', redirectTo: 'landing', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'landing', component: LandingComponent },
  { path: 'registro', component: RegistroComponent },
  // RUTA PÚBLICA (El cliente escanea el QR y entra aquí)
  { path: 'trazabilidad/:codigo', component: TrazabilidadPublicaComponent }, 

  {
    path: 'dashboard',
    component: DashboardComponent,
    children: [
      { path: '', redirectTo: 'resumen', pathMatch: 'full' },
      { path: 'resumen', component: ResumenComponent },
      { path: 'lotes', component: ListaLotesComponent },
      { path: 'lotes/nuevo', component: CrearLoteComponent },
      { path: 'lotes/:id', component: DetalleLoteComponent },
      { path: 'fincas', component: ListaFincasComponent },
      { path: 'fincas/nueva', component: CrearFincaComponent },
      { path: 'movimientos', component: ProximamenteComponent, data: { titulo: 'Movimientos' } },
      { path: 'documentos', component: ProximamenteComponent, data: { titulo: 'Documentos' } },
      { path: 'admin', component: AdminPanelComponent }
    ]
  },
  { path: '**', redirectTo: '' }
];

