import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login';
import { DashboardComponent } from './components/dashboard/dashboard';
import { ListaLotesComponent } from './components/lista-lotes/lista-lotes';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  {
    path: 'dashboard',
    component: DashboardComponent,
    children: [
      { path: '', redirectTo: 'lotes', pathMatch: 'full' },
      { path: 'lotes', component: ListaLotesComponent }
    ]
  },
  { path: '**', redirectTo: 'login' }
];