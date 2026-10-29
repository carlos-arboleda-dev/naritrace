import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login';
import { DashboardComponent } from './components/dashboard/dashboard';
import { ListaLotesComponent } from './components/lista-lotes/lista-lotes';
import { DetalleLoteComponent } from './components/detalle-lote/detalle-lote';
import { CrearLoteComponent } from './components/crear-lote/crear-lote';
import { TrazabilidadPublicaComponent } from './components/trazabilidad-publica/trazabilidad-publica';
import { ListaFincasComponent } from './components/lista-fincas/lista-fincas';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  // RUTA PÚBLICA (El cliente escanea el QR y entra aquí)
  { path: 'trazabilidad/:codigo', component: TrazabilidadPublicaComponent }, 
  {
    path: 'dashboard',
    component: DashboardComponent,
    children: [
      { path: '', redirectTo: 'lotes', pathMatch: 'full' },
      { path: 'lotes', component: ListaLotesComponent },
      { path: 'lotes/nuevo', component: CrearLoteComponent },
      { path: 'lotes/:id', component: DetalleLoteComponent },
      { path: 'fincas', component: ListaFincasComponent } 
    ]
  },
  { path: '**', redirectTo: 'login' }
];

