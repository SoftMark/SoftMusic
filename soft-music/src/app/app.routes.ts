import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { AboutComponent } from './pages/about/about.component';
import { NoteDetailComponent } from './pages/note-detail/note-detail.component';
import { MoviesComponent } from './pages/movies/movies.component';


export const routes: Routes = [
    { path: '', component: HomeComponent },
    { path: 'about', component: AboutComponent },
    { path: 'note/:id', component: NoteDetailComponent },
    { path: 'movies', component: MoviesComponent },
];
